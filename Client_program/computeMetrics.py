from ClientEncoder import FileEncoder
from ClientEncoder import argumentHandler
# Simple program to maunually close the server application if it is stuck running in the IDE.

def main():
    argHandler = argumentHandler()
    argHandler.handleArguments()
    fileLocation = './datasets_synthetic/ncvr_numrec_5000_modrec_2_ocp_0_myp_0_nump_5.csv'   
    host = argHandler.host
    port = argHandler.port
    attributeTypesList = argHandler.defineAttributeTypes()   
    encoder = FileEncoder(argHandler=argHandler)
    encoder.connectToServer(host, port) 
    
    # Connect to server and tell them to:
    encoder.send("TRUTH") # Compute ground truth + list of clusters based on rowId.
    encoder.waitForAcknowledge()
    encoder.send("METRICS")

if __name__ == "__main__":
    main()