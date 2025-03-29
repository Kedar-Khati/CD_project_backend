from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import subprocess
import sys
import os

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class GrammarInput(BaseModel):
    productions: List[str]

@app.post("/parse")
async def parse_grammar(grammar: GrammarInput):
    try:
        # Save grammar to a temporary file
        with open("temp_grammar.txt", "w") as f:
            for prod in grammar.productions:
                f.write(prod + "\n")
            f.write("end\n")
        
        # Run the CLR parser (assuming clr.py is in the same directory)
        result = subprocess.run(
            [sys.executable, "clr.py"],
            capture_output=True,
            text=True,
            input="\n".join(grammar.productions) + "\nend\n"
        )
        
        if result.returncode != 0:
            raise HTTPException(status_code=400, detail=result.stderr)
        
        # Parse the output (you'll need to modify this based on your clr.py output)
        output = parse_clr_output(result.stdout)
        
        return output
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def parse_clr_output(output: str):
    # This is a placeholder - you'll need to implement proper parsing
    # of your CLR parser's output to extract the parsing table, etc.
    lines = output.split('\n')
    
    # Extract states
    states = []
    current_state = None
    for line in lines:
        if line.startswith("Item"):
            if current_state:
                states.append(current_state)
            current_state = {"name": line.split(":")[0], "items": []}
        elif line.strip().startswith("->"):
            if current_state:
                current_state["items"].append(line.strip())
    
    if current_state:
        states.append(current_state)
    
    # Extract parsing table (simplified)
    table_start = output.find("CLR(1) TABLE")
    table_end = output.find("Enter the string to be parsed")
    table = output[table_start:table_end] if table_start != -1 else "Table not found"
    
    return {
        "states": states,
        "table": table,
        "raw_output": output
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)