import os 


def main(): 
    current = os.getcwd()
    for ent in os.walk(current + "/dev"):
            # looping in a dir by choosing the right path
            for g in os.walk(ent[0]):
                # looping only through the files
                for fi in g[2]:
                     if fi == 'en.tok.off.pos':
                        os.chdir(g[0])
                        with open(fi, encoding="utf-8") as f:
                            t = [line.split() for line in f.readlines()]
                            text = [item[3] for item in t if len(item) > 3 ]
                            text = ' '.join(text)
                            print(text)
    
    
    
if __name__ == "__main__": 
    main()
