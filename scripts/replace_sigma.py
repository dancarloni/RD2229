#!/usr/bin/env python3
"""Sostituisce in modo sicuro la parola standalone 'σ' con il simbolo 'σ'.

Regole:
- Per file Python: sostituisce solo nei token COMMENT e nelle triple-quoted STRING (docstring).
- Per file Markdown/RST/TXT: sostituisce solo al di fuori di blocchi di codice ```` ``` ````.
- Non modifica identificatori, nomi di variabili o chiavi JSON.

Uso:
    python scripts/replace_sigma.py
"""
import io 
import os 
import re 
import sys 
import tokenize 

ROOT =os .path .abspath (os .path .join (os .path .dirname (__file__ ),".."))
RE_SIGMA =re .compile (r"\bsigma\b")


def replace_in_markdown (path :str )->bool :
    changed =False 
    with open (path ,"r",encoding ="utf-8")as fh :
        lines =fh .readlines ()

    out =[]
    in_code =False 
    for ln in lines :
        stripped =ln .lstrip ()
        if stripped .startswith ("```")or stripped .startswith ("~~~"):
            in_code =not in_code 
            out .append (ln )
            continue 
        if in_code :
            out .append (ln )
            continue 
        new =RE_SIGMA .sub ("σ",ln )
        if new !=ln :
            changed =True 
        out .append (new )

    if changed :
        with open (path ,"w",encoding ="utf-8")as fh :
            fh .writelines (out )
    return changed 


def replace_in_python (path :str )->bool :
    changed =False 
    with open (path ,"rb")as fh :
        src =fh .read ()

    try :
        tokens =list (tokenize .tokenize (io .BytesIO (src ).readline ))
    except Exception :
        return False 

    out_tokens =[]
    for tok in tokens :
        ttype =tok .type 
        tstring =tok .string 
        if ttype ==tokenize .COMMENT :
            new =RE_SIGMA .sub ("σ",tstring )
            if new !=tstring :
                changed =True 
                tstring =new 
            out_tokens .append ((ttype ,tstring ))
        elif ttype ==tokenize .STRING :
        # Heuristic: modify only triple-quoted strings (likely docstrings)
            if tstring .startswith (('"""',"'''")):
            # remove quotes, replace, rewrap
                quote =tstring [:3 ]
                inner =tstring [3 :-3 ]
                new_inner =RE_SIGMA .sub ("σ",inner )
                if new_inner !=inner :
                    changed =True 
                    tstring =quote +new_inner +quote 
            out_tokens .append ((ttype ,tstring ))
        else :
            out_tokens .append ((ttype ,tstring ))

    if not changed :
        return False 

        # Reconstruct bytes
    try :
        new_src =tokenize .untokenize (out_tokens )
        if isinstance (new_src ,str ):
            new_src =new_src .encode ("utf-8")
        with open (path ,"wb")as fh :
            fh .write (new_src )
    except Exception :
        return False 
    return True 


def main ():
    changed_files =[]
    for dirpath ,dirnames ,filenames in os .walk (ROOT ):
    # skip virtual envs, .git, data binary directories
        if ".git"in dirpath .split (os .sep ):
            continue 
        for fn in filenames :
            path =os .path .join (dirpath ,fn )
            if fn .endswith (".md")or fn .endswith (".rst")or fn .endswith (".txt"):
                if replace_in_markdown (path ):
                    changed_files .append (path )
            elif fn .endswith (".py"):
                if replace_in_python (path ):
                    changed_files .append (path )

    if changed_files :
        print ("Files modified:")
        for p in changed_files :
            print (" -",os .path .relpath (p ,ROOT ))
    else :
        print ("No safe occurrences of 'sigma' replaced.")


if __name__ =="__main__":
    main ()
