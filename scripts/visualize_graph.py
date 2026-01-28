import sys
import os
from dotenv import load_dotenv

# Load env vars first
load_dotenv()

# Set up path to find src module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

try:
    from src.agents.graph import create_zipsa_graph
    
    graph = create_zipsa_graph()
    png_data = graph.get_graph().draw_mermaid_png()
    
    output_path = os.path.join(os.path.dirname(__file__), "graph_visualization.png")
    with open(output_path, "wb") as f:
        f.write(png_data)
        
    print(f"Graph visualization saved to: {output_path}")
    
except Exception as e:
    print(f"Error visualizing graph: {e}")
    # Fallback to print mermaid code if png fails (needs graphviz)
    try:
        print("\nMermaid Code:")
        print(graph.get_graph().draw_mermaid())
    except:
        pass
