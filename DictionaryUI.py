from __future__ import annotations

try:
    import httpx
except ImportError:
    raise ImportError("Please install httpx with 'pip install httpx' ")

import json
import logging
# create logger with DictionaryUI
logger = logging.getLogger("DictionaryUI")
logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
fh = logging.FileHandler("dictionary.log")
fh.setLevel(logging.DEBUG)
logger.addHandler(fh)
from pprint import pprint
import re
import string
from textual import work
from textual.app import App, ComposeResult
from textual.containers import VerticalScroll, HorizontalScroll, Container
from textual.widgets import Input, Markdown, Footer, Label

def QueryPacker(queryLIST, dictionary, dictSTR="amis"):
    resultLIST = []
    if dictSTR == "amis":
        for q in queryLIST:
            if q in dictionary:
                for content in dictionary[q]["definitions"]:
                    resultLIST.append("## Definition:")
                    resultLIST.append(content["def"])
                    resultLIST.append("============")
                    try:
                        resultLIST.append("## Synonyms:")
                        resultLIST.append("\n".join(content["synonyms"]))
                    except:
                        pass
    elif dictSTR == "siraya":
        for q in queryLIST:
            if q in dictionary:
                resultLIST.append("## Definition:")
                resultLIST.append(q["definitions"][0]["def"])
                resultLIST.append("## Synonyms:")
                resultLIST.append("\n".join(q["definitions"][0]["synonyms"]))
                resultLIST.append("============")
    return resultLIST

def FuzzyQueryMaker(word, dictionary, dictSTR="amis"):
    resultLIST = []
    patternDICT = {"C":"[bcdfghjklmnpqrstvxz]",
                   "V":"[aeiuowyj]",
                   "N":"([mn]|ng)",
                   "L":"[rl]",
                   "B":"[bpdtkg]"
                   }
    #NaV => ["mab", "map", "mad", "mat"...]
    #Bob
    queryLIST = []
    for char in word:
        if char in patternDICT:
            queryLIST.append(patternDICT[char])  #[bpdtkg]
        else:
            queryLIST.append(char)               #[bpdtkg]ob
    querySTR = "".join(queryLIST)
    queryPat = re.compile(querySTR)
    keySTR = "\n".join([k for k in dictionary])
    matches = set([q.group(0) for q in queryPat.finditer(keySTR)]) #queryPat.findall(k) != []:
    matches = sorted(matches)
    if matches:
        for k in matches:
            if dictSTR == "amis":
                try:
                    for content in dictionary[k]["definitions"]:
                        resultLIST.append(f"## Match Entry: {k}")
                        resultLIST.append("## Definition:")
                        resultLIST.append(content["def"])
                        resultLIST.append("============")
                        try:
                            resultLIST.append("## Synonyms:")
                            resultLIST.append("\n".join(content["synonyms"]))
                        except:
                            pass
                except:
                    pass
            elif dictSTR == "siraya":
                try:
                    resultLIST.append(f"## Match Entry: {k}")
                    resultLIST.append("## Definition:")
                    resultLIST.append(dictionary[k]["definitions"][0]["def"])
                    resultLIST.append("## Synonyms:")
                    resultLIST.append("\n".join(dictionary[k]["definitions"][0]["synonyms"]))
                    resultLIST.append("============")
                except:
                    pass
    return resultLIST

def regex_search(word, dictionary, resultLIST, is_amis=True):
    patternDICT = {"C":"[bcdfghjklmnpqrstvxz]",
                   "V":"[aeiuowyj]",
                   "N":"([mn]|ng)",
                   "L":"[rl]",
                   "B":"[bpdtkg]"
                   }
    #NaV => ["mab", "map", "mad", "mat"...]
    #Bob
    queryLIST = []
    for char in word:
        if char in patternDICT:
            queryLIST.append(patternDICT[char])  #[bpdtkg]
        else:
            queryLIST.append(char)               #[bpdtkg]ob
    querySTR = "".join(queryLIST)
    #logger.debug(querySTR)
    queryPat = re.compile(querySTR)
    keySTR = "\n".join([k for k in dictionary])
    matches = set([q.group(0) for q in queryPat.finditer(keySTR)]) #queryPat.findall(k) != []:
    matches = sorted(matches)
#    try:
        #logger.debug(matches)
    if matches:
        for k in matches:
            #resultLIST.append(f"## Match: {k}")
            if is_amis:
                try:
                    for i in dictionary[k]["definitions"]:
                        resultLIST.append("## Definition:")
                        resultLIST.append(i["def"])
                        resultLIST.append("============")
                        try:
                            resultLIST.append("## Synonyms:")
                            resultLIST.append("\n".join(i["synonyms"]))
                        except:
                            pass
                except KeyError:
                    for entry in dictionary:
                        if k in entry:
                            resultLIST.append(f"## Match Entry: {entry}")
                            for i in dictionary[entry]["definitions"]:
                                    resultLIST.append("## Definition:")
                                    resultLIST.append(i["def"])
                                    try:
                                        resultLIST.append("## Synonyms:")
                                        resultLIST.append("\n".join(i["synonyms"]))
                                    except:
                                        pass                              
            else:
                try:
                    resultLIST.append("## Definition:")
                    resultLIST.append(dictionary[k]["definitions"][0]["def"])
                    resultLIST.append("## Synonyms:")
                    resultLIST.append("\n".join(dictionary[k]["definitions"][0]["synonyms"]))
                    resultLIST.append("============")
                except KeyError:
                    for entry in dictionary:
                        if k in entry:
                            resultLIST.append(f"## Match Entry: {entry}")
                            resultLIST.append("## Definition:")
                            resultLIST.append(dictionary[entry]["definitions"][0]["def"])
                            resultLIST.append("## Synonyms:")
                            resultLIST.append("\n".join(dictionary[entry]["definitions"][0]["synonyms"]))
                            resultLIST.append("============")
    else:
        pass
        #resultLIST.append("ENTRY NOT FOUND")

    #except Exception as e:
        #resultLIST.append(f"UNKNOWN ERROR: {str(e)}")

def load_amis_dictionary(file_path: str) -> dict:
    data = json.load(open(file_path, encoding="utf-8"))
    result = {f"{item['title']}": {
        "definitions": [
            {
                "synonyms": definition.get("synonyms", []),
                "def": definition.get("def", "").replace("￻", " ").replace("￹", " ").replace("￺", " ")
            }
            for definition in item["heteronyms"][0].get("definitions", [])
        ]
    }
    for item in data}
    return result

def load_siraya_dictionary(file_path: str) -> dict:
    data = json.load(open(file_path, encoding="utf-8"))
    result = {f"{item['title']}": {
        "definitions": item["heteronyms"][0].get("definitions", [])}
    for item in data}
    return result

class DictionaryApp(App):
    """Searches a dictionary API as-you-type."""

    CSS_PATH = "css/dictionary.tcss"
    BINDINGS = [
        ("ctrl+q", "quit", "Quit"),
    ]
    def compose(self) -> ComposeResult:
        # <Need more work here>
        yield Input(placeholder="Search for a word")
        with HorizontalScroll(id="head-container"):
            with Container(classes="head"):
                yield Label("Amis Dictionary")
            with Container(classes="head"):
                yield Label("Siraya Dictionary")
        # </Need more work here>

        with HorizontalScroll(id="results-container"):
            with VerticalScroll(classes="scroll"):
                yield Markdown(id="amis-results")
            with VerticalScroll(classes="scroll"):
                yield Markdown(id="siraya-results")
        yield Footer()


    async def on_input_changed(self, message: Input.Changed) -> None:
        """A coroutine to handle a text changed message."""
        if message.value:
            #self.lookup_word(message.value)
            self.lookup_dictionary(message.value)
        else:
            # Clear the results
            await self.query_one("#amis-results", Markdown).update("")
            await self.query_one("#siraya-results", Markdown).update("")


# #Do our look-up here!   .*kan.*
    @work(exclusive=True)
    async def lookup_dictionary(self, word: str) -> None:  #if "[" "]" "_" "CVN" => string ; => regex
        resultLIST = []
        resultLIST.append("# 🅰️ mis Dictionary")
        def process_dictionary(word, dictionary, resultLIST):
            if word in dictionary:
                for i in dictionary[word]["definitions"]:
                    resultLIST.append("## Definition:")
                    resultLIST.append(i["def"])
                    try:
                        resultLIST.append("## Synonyms:")
                        resultLIST.append("\n".join(i["synonyms"]))
                    except:
                        pass
            #<regex search here>
            else:
                regex_search(word, dictionary, resultLIST, is_amis=True)
            #</regex search here>
        #logger.debug(amisDICT_01)
        process_dictionary(word, amisDICT_01, resultLIST)
        process_dictionary(word, amisDICT_02, resultLIST)
        if word == self.query_one(Input).value:
            #markdown = self.make_word_markdown("\n".join(resultLIST))
            self.query_one("#amis-results", Markdown).update("\n".join(resultLIST))
            if set("CVNLB").intersection(word):
                resultLIST = FuzzyQueryMaker(word)
            elif
            
            else:
                resultLIST = MatchingQuery(word)
                
        resultLIST = []
        resultLIST.append("# 🇸 iraya Dictionary #")
        def process_siraya_dictionary(word, dictionary, resultLIST):
            if word in dictionary:
                resultLIST.append("## Definition:")
                resultLIST.append(dictionary[word]["definitions"][0]["def"])
                resultLIST.append("## Synonyms:")
                resultLIST.append("\n".join(dictionary[word]["definitions"][0]["synonyms"]))
            #<regex search here>
            else:
                regex_search(word, dictionary, resultLIST, is_amis=False)
            #</regex search here>
        process_siraya_dictionary(word, sirayaDICT_01, resultLIST)
        process_siraya_dictionary(word, sirayaDICT_02, resultLIST)

        if word == self.query_one(Input).value:
            #markdown = self.make_word_markdown("\n".join(resultLIST))
            self.query_one("#siraya-results", Markdown).update("\n".join(resultLIST))


    @work(exclusive=True)
    async def lookup_word(self, word: str) -> None:
        """Looks up a word."""
        url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"

        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            try:
                results = response.json()
            except Exception:
                self.query_one("#results", Markdown).update(response.text)
                return

        if word == self.query_one(Input).value:
            markdown = self.make_word_markdown(results)
            self.query_one("#results", Markdown).update(markdown)

    def make_word_markdown(self, results: object) -> str:
        """Convert the results in to markdown."""
        lines = []
        if isinstance(results, dict):
            lines.append(f"# {results['title']}")
            lines.append(results["message"])
        elif isinstance(results, list):
            for result in results:
                lines.append(f"# {result['word']}")
                lines.append("")
                for meaning in result.get("meanings", []):
                    lines.append(f"_{meaning['partOfSpeech']}_")
                    lines.append("")
                    for definition in meaning.get("definitions", []):
                        lines.append(f" - {definition['definition']}")
                    lines.append("---")

        return "\n".join(lines)


if __name__ == "__main__":

    amisDICT_01 = load_amis_dictionary("dictionary/dict-amis.json")
    amisDICT_02 = load_amis_dictionary("dictionary/dict-amis-safolu.json")
    #amisDICT_03 = load_dictionary("dictionary/dict-concised.audio.json")
    sirayaDICT_01 = load_siraya_dictionary("dictionary/dict.jenny.json")
    sirayaDICT_02 = load_siraya_dictionary("dictionary/dict.jenny2.json")

    #app = DictionaryApp()
    #app.run()
    
    word = "NaCa"
    f = FuzzyQueryMaker(word, amisDICT_01)
    pprint(f)