/**
 * proxy/server.js
 *
 * Express proxy server — Vite-compatible equivalent of the Next.js proxy middleware.
 *
 * What it does (mirrors the original Next.js proxy):
 *  1. Reads the Supabase session from the "Authorization: Bearer <token>" header
 *  2. Calls supabase.auth.getUser(token) to validate the JWT (refreshes if needed)
 *  3. Returns 401 JSON for unauthenticated callers hitting /protected routes
 *  4. Forwards all other requests to the target (Vite dev server OR Python backend)
 *
 * Ports:
 *  - Proxy listens on  :3001
 *  - Vite dev server   :5173
 *  - Python backend    :5000
 *
 * Run:  npm run proxy   (or  node proxy/server.js)
 */

import express from "express";
import cors from "cors";
import { createProxyMiddleware } from "http-proxy-middleware";
import { createClient } from "@supabase/supabase-js";
import dotenv from "dotenv";
import path from "path";
import { fileURLToPath } from "url";

// -- Load .env from the frontend root ---------------------------------
const __dirname = path.dirname(fileURLToPath(import.meta.url));
dotenv.config({ path: path.resolve(__dirname, "../.env") });

// -- Supabase client (server-side / JWT validation) --------------------
const SUPABASE_URL      = process.env.NEXT_PUBLIC_SUPABASE_URL;
const SUPABASE_ANON_KEY = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

if (!SUPABASE_URL || !SUPABASE_ANON_KEY) {
  console.error(
    "[proxy] ?  Missing NEXT_PUBLIC_SUPABASE_URL or NEXT_PUBLIC_SUPABASE_ANON_KEY in .env"
  );
  process.exit(1);
}

const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY, {
  auth: {
    persistSession:      false, // stateless — validate per-request JWT
    autoRefreshToken:    false,
    detectSessionInUrl:  false,
  },
});

const app            = express();
const PROXY_PORT     = process.env.PROXY_PORT    || 3001;
const VITE_TARGET    = process.env.VITE_TARGET   || "http://localhost:5173";
const BACKEND_TARGET = process.env.BACKEND_TARGET || "http://localhost:5000";

// -- CORS --------------------------------------------------------------
app.use(
  cors({
    origin: [VITE_TARGET, "http://localhost:5173", "http://127.0.0.1:5173"],
    credentials: true,
  })
);

// -- Auth helper -------------------------------------------------------
/**
 * Extracts the bearer token from "Authorization: Bearer <token>"
 * and verifies it with Supabase — identical to how Next.js middleware
 * calls supabase.auth.getUser() to refresh/validate the session.
 *
 * @param {import("express").Request} req
 * @returns {Promise<object|null>} Supabase user object or null
 */
async function getUserFromRequest(req) {
  const authHeader = req.headers["authorization"] || "";
  const token      = authHeader.startsWith("Bearer ")
    ? authHeader.slice(7).trim()
    : null;

  if (!token) return null;

  const {
    data: { user },
    error,
  } = await supabase.auth.getUser(token);

  if (error) {
    console.warn("[proxy] Auth token validation failed:", error.message);
    return null;
  }

  console.log("[proxy] Authenticated user:", { user });
  return user;
}

// -- Auth-gating middleware --------------------------------------------
/**
 * Mirrors the exported proxy() function from the original Next.js middleware:
 *  - /protected/* routes require a valid Supabase session
 *  - All other routes pass through without auth check
 *
 * @param {import("express").Request}  req
 * @param {import("express").Response} res
 * @param {import("express").NextFunction} next
 */
async function authGate(req, res, next) {
  const pathname = req.path;

  if (!pathname.startsWith("/protected")) {
    return next(); // public route — skip auth check
  }

  const user = await getUserFromRequest(req);

  if (!user) {
    console.log(`[proxy] ?? Blocked unauthenticated access to ${pathname}`);
    // Mirror Next.js redirect: in a REST proxy context return 401 + redirect hint
    return res.status(401).json({
      error:      "Unauthenticated",
      message:    "You must be logged in to access this route.",
      redirectTo: "/login",
    });
  }

  req.user = user; // attach to request for downstream handlers
  next();
}

app.use(authGate);

// -- Route: /api/* ? Python backend (port 5000) -----------------------
app.use(
  "/api",
  createProxyMiddleware({
    target:       BACKEND_TARGET,
    changeOrigin: true,
    on: {
      error: (err, _req, res) => {
        console.error("[proxy] Backend proxy error:", err.message);
        res.status(502).json({ error: "Backend unreachable", detail: err.message });
      },
    },
  })
);

// -- Route: everything else ? Vite dev server (port 5173) -------------
app.use(
  "/",
  createProxyMiddleware({
    target:       VITE_TARGET,
    changeOrigin: true,
    ws:           true, // WebSocket for Vite HMR
    on: {
      error: (err, _req, res) => {
        console.error("[proxy] Vite proxy error:", err.message);
        if (!res.headersSent) {
          res.status(502).json({ error: "Vite server unreachable", detail: err.message });
        }
      },
    },
  })
);

// -- Start -------------------------------------------------------------
app.listen(PROXY_PORT, () => {
  console.log(`
  +------------------------------------------------------+
  ¦       Orchestrator AI — Auth Proxy Server           ¦
  ¦------------------------------------------------------¦
  ¦  ?? Proxy        : http://localhost:${PROXY_PORT}           ¦
  ¦  ? Vite target  : ${VITE_TARGET}      ¦
  ¦  ?? Backend      : ${BACKEND_TARGET}      ¦
  ¦  ?? Gating       : /protected/*                     ¦
  +------------------------------------------------------+
  `);
});

export default app;
