/**
 * src/lib/supabase.js
 *
 * Singleton Supabase browser client.
 *
 * Supabase automatically persists the session in localStorage under the key
 * "sb-<project-ref>-auth-token", so the user stays logged in across page
 * refreshes / browser restarts until they explicitly call signOut().
 */
import { createClient } from "@supabase/supabase-js";

const supabaseUrl  = import.meta.env.VITE_SUPABASE_URL;
const supabaseKey  = import.meta.env.VITE_SUPABASE_ANON_KEY;

if (!supabaseUrl || !supabaseKey) {
  throw new Error(
    "[supabase] Missing VITE_SUPABASE_URL or VITE_SUPABASE_ANON_KEY in .env"
  );
}

export const supabase = createClient(supabaseUrl, supabaseKey, {
  auth: {
    // Keep the session in localStorage so the user stays logged in
    persistSession:   true,
    // Automatically refresh the JWT before it expires
    autoRefreshToken: true,
    // Detect the #access_token fragment Supabase adds after email verification
    detectSessionInUrl: true,
    storageKey: "orchestrator-session",
  },
});
