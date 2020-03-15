from googletrans import Translator
import os

IGNORE_FOLDERS = ['scripts', '.git']

def main(lang):
    file_content = texto_inicial(lang=lang)
    file_content += criar_lista(lang=lang)
    file_content += text_final(lang=lang)
    
    with open("test_{0}.md".format(lang), "w") as f:
        f.write(file_content)

def texto_inicial(lang='pt'):
    try:
        with open("data/texto_inicial_{0}.txt".format(lang), "r") as f:
            return f.read()
    except OSError:
        raise Exception("Linguagem \"{0}\" não suportada.".format(lang))

def text_final(lang='pt'):
    try:
        with open("data/texto_final_{0}.txt".format(lang), "r") as f:
            return f.read()
    except OSError:
        raise Exception("Linguagem \"{0}\" não suportada.".format(lang))
    
def capitalizar_primeira_letra(string):
    l = list(string)

    l[0] = l[0].upper()

    return ''.join(l)

def criar_lista(lang='pt'):
    global IGNORE_FOLDERS
    
    dirs = [name for name in os.listdir("..") if os.path.isdir("../" + name)]

    dirs.sort()
    
    trslt = Translator()
    
    if lang != 'pt':
        text = '\n## {0}\n'.format(trslt.translate("Lista", src='pt', dest=lang).text)
    else:
        text = '\n## Lista\n'
    
    for d in dirs:
        if d in IGNORE_FOLDERS:
            continue

        if lang == 'pt':
            d_name = d
        else:
            d_name = trslt.translate(d, src='pt', dest=lang).text

        d_name = capitalizar_primeira_letra(d_name)
        
        folder_link = "https://github.com/Marcos-Costa/awesome-ufma/tree/master/{0}".format(d.replace(' ', '%20'))
    
        aux_text = "- [{0}]({1})\n".format(d_name, folder_link)

        f_dirs = [name for name in os.listdir("../" + d) if os.path.isdir("../" + d + "/" + name)]

        f_dirs.sort()
        
        for f_d in f_dirs:
            if lang == 'pt':
                f_d_name = f_d
            else:
                f_d_name = trslt.translate(f_d, src='pt', dest=lang).text

                if lang == 'en':
                    f_d_name.replace('Proof', 'Test')

            f_d_name = capitalizar_primeira_letra(f_d_name)
                
            aux_text += "    - [{0}]({1}/{2})\n".format(f_d_name, folder_link, f_d.replace(' ', '%20'))

        text += aux_text

    return text + '\n'
    
if __name__ == '__main__':    
    main('pt')
    main('en')
