from graph.builder import build_workflow


def main():
    app = build_workflow()

    graph = app.get_graph()

    print("\n==============================")
    print("   AGENTIC AI ORCHESTRATOR")
    print("==============================\n")

    # ASCII Graph
    try:
        print(graph.draw_ascii())
    except Exception as e:
        print("ASCII visualization failed:", e)

    # Mermaid Graph
    try:
        print("\n========== MERMAID ==========\n")
        print(graph.draw_mermaid())
    except Exception as e:
        print("Mermaid generation failed:", e)

    # PNG Graph
    try:
        png = graph.draw_mermaid_png()

        with open("workflow_graph.png", "wb") as f:
            f.write(png)

        print("\n✅ workflow_graph.png generated successfully!")
    except Exception as e:
        print("\nPNG generation failed.")
        print(e)


if __name__ == "__main__":
    main()