# -*- coding: utf-8 -*-

import re
import os

RESERVED = "ø"
HEAD_LATEX = r"""
\documentclass[a4paper,11pt]{article}
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage{lmodern}
\usepackage[francais]{babel}
\usepackage{array}
\usepackage{"""+os.path.join(os.getcwd(),"tex","xargs")+r"""}
\usepackage{tikz}
\usepackage{"""+os.path.join(os.getcwd(),"tex","ltablex")+r"""}
\usepackage{"""+os.path.join(os.getcwd(),"tex","fancybox")+r"""}
\usepackage[bottom=1cm,right=1.5cm,left=1.5cm,top=1cm]{geometry}
\usepackage{"""+os.path.join(os.getcwd(),"tex","graphicx")+r"""}
\usepackage{"""+os.path.join(os.getcwd(),"tex","multirow")+r"""}
\usepackage{nopageno}
\usepackage{hyperref}


\let\oldUp\up
\def\up{\monter}
\def\down{\descendre}
\def\Up{\Monter}
\def\Down{\Descendre}
\def\dow{\down}
\def\Dow{\Down}


\newcommand{\num}[1]{n$^o$ #1}
\renewcommandx{\top}[3]{\let\oldUp\up \def\up{\monter} \multirow{#3}{*}{\num{\thenumTop}}& \addtocounter{numTop}{1} \ifnum#3=1 #1 \else \multirow{#3}{6cm}{#1} \fi & #2 \\ \hline}
\newcommand{\et}[1]{& & #1 \\}
\newcommandx{\subnum}[1]{\resizebox{!}{!}{\tikz[baseline=(char.base)]{\node[shape=circle,draw,inner sep=1pt] (char) {\ifnum#1>9 #1 \else 0#1 \fi};}}}
\newcommandx{\flash}[1][1=0]{\doublebox{FLASH}\ifnum#1>0 \ensuremath{^{#1\%}}\fi~}
\newcommandx{\solo}[1][1=0]{\doublebox{SOLO}\ifnum#1>0 \ensuremath{^{#1\%}}\fi~}
\newcommand{\piste}[1]{ \let\oldUp\up \def\up{\monter}\fbox{\ifnum#1<10 0\fi#1}}
\newcommandx{\monter}[1][1=0]{$\nearrow$\ifnum#1>0 $^{#1\%}$ \fi}
\newcommandx{\descendre}[1][1=0]{$\searrow$\ifnum#1>0 $_{#1\%}$ \fi}
\newcommandx{\Monter}[1][1=0]{$\Uparrow$\ifnum#1>0 $^{#1\%}$ \fi}
\newcommandx{\Descendre}[1][1=0]{$\Downarrow$\ifnum#1>0 $_{#1\%}$ \fi}
\newcommand{\noir}{\resizebox{!}{10pt}{\shadowbox{NOIR}}}
\newcommand{\start}{\fbox{\small{START}}}
\newcommand{\sub}[1]{\let\oldUp\up \def\up{\monter}\subnum{#1}}
\newcommand{\banque}[1]{{\setlength{\fboxsep }{1pt}\doublebox{\small{\ifnum#1<10 0\fi#1}}}}
\newcommand{\comment}[1]{\hfill{\scalebox{0.6}{(#1)}}}
\newcommand{\passur}[1]{{\color{red}{\comment{#1}}}}
\newcommandx{\topupdown}[4][4=0]{\top{#1}{#2}[#4][2][\et{#3}]}
\renewcommand{\special}[1]{\scalebox{0.7}{\ovalbox{#1}}}

\newcommand{\twodigitformat}[1]{\ifnum#1>9 #1\else 0#1\fi}

\newcommandx{\entete}[5][3= ,4= ,5=1]{\ifnum#5=0 \vspace{10pt} \fi \subnum{\thenumPartie}\hspace{10pt}\ifnum#5=1 \textbf{#1}\fi\hspace{10pt}\ifnum#5=1 \subnum{\thenumPartie}\vspace{10pt}\fi\\ \begin{tabular}{|l|c|r|} \hline  Avant\hspace{2cm} & \hspace{2cm}Banque\hspace{2cm} & \hspace{2cm}Après \\ \hline  \small{#3} & n$^o$ #2 & \small{#4} \\ \hline \end{tabular} \vspace{10pt} \ifnum#5=0 \newpage \fi}
"""

def parse_sub(CHAINE):
    CHAINE = re.sub(r'\(([0-9]+)\)',r'\\sub{\1}', CHAINE)
    return CHAINE

def parse_piste(CHAINE):
    CHAINE = re.sub(r'\[([0-9]+)\]',r'\piste{\1}', CHAINE)
    return CHAINE

def parse_updown(CHAINE):
    CHAINE = re.sub(r'u',r'\\up ',CHAINE)
    CHAINE = re.sub(r'U',r'\\Up ',CHAINE)
    CHAINE = re.sub(r'd',r'\\dow ',CHAINE)
    CHAINE = re.sub(r'D',r'\\Dow ',CHAINE)
    return CHAINE

def parse_param(CHAINE): 
    CHAINE = re.sub(r'_([0-9]+)',r'[\1]', CHAINE)
    return CHAINE

def parse_comment(CHAINE):
    match = re.findall(r'\".*?\"', CHAINE)
    comment = ""
    for find in match:
        comment += "\\comment{"+find[1:-1]+"}"
    CHAINE = re.sub(r'\".*?\"', r'', CHAINE)
    return CHAINE,comment

def parse_special_start(CHAINE):
    global RESERVED
    match = re.findall(r'\{.*?\}', CHAINE)
    special = []
    for find in match:
        special.append("\\special{"+find[1:-1]+"}")
        CHAINE = re.sub(r'\{'+find[1:-1]+r'\}', RESERVED+str(len(special)-1)+RESERVED, CHAINE, count=1)
    return CHAINE,special

def parse_special_end(CHAINE,special):
    global RESERVED
    for index,elem in enumerate(special):
        patern = RESERVED+str(index)+RESERVED
        CHAINE = re.sub(r'('+patern+')', elem, CHAINE)
    return CHAINE

def parse_other(CHAINE):
    CHAINE = re.sub(r'n',r'\\noir ',CHAINE)
    CHAINE = re.sub(r's',r'\\solo ',CHAINE)
    CHAINE = re.sub(r'f',r'\\flash ',CHAINE)
    return CHAINE

def parse_protect(CHAINE):
    CHAINE = re.sub(r'%','\\%',CHAINE)
    CHAINE = re.sub(r'\\','\\\\',CHAINE)
    return CHAINE

def parse_all(chaine):
    chaine = parse_protect(chaine)
    chaine,comment = parse_comment(chaine)
    chaine,special = parse_special_start(chaine)
    chaine = parse_updown(chaine)
    #chaine = parse_other(chaine)
    chaine = parse_sub(chaine)
    chaine = parse_piste(chaine)
    chaine = parse_param(chaine)
    chaine = parse_special_end(chaine,special)
    return chaine,comment

def transform(CHAINE):
    result = []
    if CHAINE == "":
        return result
    for chaine in CHAINE.split(";"):
        chaine,comment = parse_all(chaine)
        result.append(chaine+comment)
    return result

def compile_section(section,before,after):
    dictionary = {"title": section.name, "bank": section.bank, "before_title": before[0], "before_bank": before[1], "after_title": after[0], "after_bank": after[1]}
    latex = r"""
\setcounter{numTop}{1}
\def\titre{%(title)s}
\def\numbanque{%(bank)d}
\def\avant{%(before_title)s \banque{%(before_bank)d}}
\def\apres{%(after_title)s \banque{%(after_bank)d}}

\begin{center}
\pdfbookmark{(\twodigitformat{\numbanque}) ~ \titre}{\thenumPartie}
\entete{\titre}{\numbanque}[\avant][\apres]

{\renewcommand{\arraystretch}{1.3}
\keepXColumns
\begin{center}
\begin{tabularx}{15cm}{|c||m{7cm}|X|} \hline                                                    
 & Description du top & Action à faire  \\  \hline  \hline \endfirsthead """ % dictionary

    for top in section.tops:
        latex += "\n" + compile_top(top)
    
    latex += r"""
\end{tabularx}
\end{center}}

\entete{}{\numbanque}[\avant][\apres][0]
\addtocounter{numPartie}{1}

\end{center}
"""
    return latex

def compile_top(top):
    tops = list(top.get_latex())
    n = len(tops)
    tops = """\\\\&&""".join(tops)
    return "\\top{"+top.top+"}{"+tops+"}{"+str(n)+"}"

def compile_only_top(top):
    global HEAD_LATEX
    latex = HEAD_LATEX
    latex += r"""
    \begin{document}"""
    tops = list(top.get_latex())
    tops = "\\".join(tops)
    latex += tops
    latex += r"""
    \end{document}"""
    return latex

def compile_conduite(conduite):
    global HEAD_LATEX
    latex = HEAD_LATEX
    latex += r"""
\newcounter{numPartie} 
\setcounter{numPartie}{1} 
\begin{document} 

\newcounter{numTop} """

    latex += "\n" + conduite.compile_section()
    
    latex += r"""
    %\pdfbookmark{Fin de la conduite}{Fin de la conduite}
    \end{document}
    """
    
    return latex

def get_subs(CHAINE):
    subs = []
    match = True
    while match is not None:
        match = re.match(r'(\(([0-9]+)\))([ud])', CHAINE)
        for find in match.groups():
            print(find)
            #subs.append(find[1:-1]) # ajout du sub trouvé
    return subs

def get_pistes(CHAINE):
    pistes = []
    match = re.findall(r'\[[0-9]+\]"', CHAINE)
    for find in match:
        pistes.append(find[1:-1]) # ajout de la liste trouvé
    return pistes

if __name__ == '__main__':
    chaine = "(10)u{special}{special2}[10]d(5)d(3)u"
    print(get_subs(chaine))
    