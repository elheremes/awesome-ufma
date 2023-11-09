import os, re
from google.cloud import translate_v3beta1
from google.cloud.translate_v3beta1 import TranslateTextResponse

files = {}
languages = {}  # Idiomas disponíveis
modules = {}  # Módulos disponíveis

""" Definição do sistema de templates
    {% nome = var %} = Atribuição de variável
    {# #} = Comentário
    {{ }} = Importar módulo
"""


def open_template(path: str) -> str:
    try:
        with open(path, "r") as f:
            arq = f.read()
            f.close()
            return arq
    except OSError:
        raise Exception("Failed to read file", path)


def extractLanguagesAndModules(path: str) -> tuple[dict, dict, dict]:
    files = os.listdir(path)
    texts = {}
    languages = {}
    modules = {}

    for file in files:
        text = open_template(path + "/" + file)

        # Get variables and filtered text from file
        variables, text = getTemplateVariables(text)

        # Prepare for add to dict
        match variables['type']:
            case 'language':
                selected = languages
            case 'module':
                selected = modules
            case _:
                raise Exception(f"File {file}: Unknown value for type({variables['type']})")

        # Adds to selected dict
        selected[variables['shortname']] = variables
        texts[variables['shortname']] = text

    return texts, languages, modules


def getTemplateVariables(text: str) -> tuple[dict, str]:
    # Procura por todo caso que se encaixa em {% <nome_var> = <valor_var> %}
    # Espaços entre os tokens são ignorados
    variables = dict(re.findall(r'(?<={%) *(.*?) *= *(.*?) *(?=%})', text))
    # Remove as variáveis do texto Final
    ret = text[:]
    ret = re.sub(r'({%)(.*?)(%}\n?)', '', ret)
    return variables, ret


def generateLangList(languageList: dict) -> str:
    text = []
    for lang in languageList.values():
        _ = f"[{lang['name']}](README_{lang['shortname']}.md)"
        text.append(f"[{lang['name']}](README_{lang['shortname']}.md)")
    return ','.join(text)


def generateDirNames(path: str) -> dict:
    blacklist = ['venv', 'scripts', '.git', '.idea', '.vscode']
    availableDir = [name for name in os.listdir(path) if os.path.isdir(path + name) and name not in blacklist]
    ret = {}

    for directory in availableDir:
        ret[directory] = [name for name in os.listdir(f"{path}/{directory}") if
                          os.path.isdir(f"{path}/{directory}/{name}")]

    return ret


def concatDirNames(dirTree: dict) -> str:
    ret = []
    for folder in dirTree.keys():
        _ = f"- [{folder}]({folder.replace(' ', '%20')})\n"
        for subfolder in dirTree[folder]:
            _ += f"\t- [{subfolder}]({folder.replace(' ', '%20')}/{subfolder.replace(' ', '%20')})\n"
        ret.append(_)
    return '\n'.join(ret)


def substituteModules(text: str, availableModules: dict, availableFiles: dict, dirTree: dict, language: str) -> str:
    modules = re.findall('(?<={{) *(.*?) *(?=}})', text)
    ret = text[:]
    for module in modules:
        if module in availableModules.keys():
            ret = re.sub(f"({{{{) *{module} *(}}}})", availableFiles[module], ret)
        elif module == 'list':
            pass  # Implement translation
        else:
            raise Exception(f"Module {module} not found")
    return ret


def writeFile(text, path):
    with open(path, 'w') as f:
        f.write(text)
        f.close()


def remove_comments(text: str):
    """Remove everything that is between {# #}"""
    regex = r'([\n]?{#)(.*?)(#}[\n]?)'
    return re.sub(regex, '', text)


if __name__ == '__main__':
    # Filters
    files, languages, modules = extractLanguagesAndModules("./templates")

    # Get list of languages
    files['otherLanguages'] = generateLangList(languages)
    modules['otherLanguages'] = {}

    # Get list of directories. This will be translated
    dirTree = generateDirNames('../')

    # Dummy for no internet mode
    files['list'] = concatDirNames(dirTree)
    modules['list'] = {}

    for file in languages.keys():
        files[file] = remove_comments(files[file])
        files[file] = substituteModules(files[file], modules, files, dirTree, file)
        writeFile(files[file], "../README_" + file + ".md")
