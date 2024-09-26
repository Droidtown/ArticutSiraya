from __future__ import annotations

#from Lib.unittest import result

#try:
    #import httpx
#except ImportError:
    #raise ImportError("Please install httpx with 'pip install httpx' ")

import json
import logging
# create logger with DictionaryUI
logger = logging.getLogger("DictionaryUI")
logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
fh = logging.FileHandler("dictionary.log")
fh.setLevel(logging.DEBUG)
logger.addHandler(fh)
#from pprint import pprint
import re
#import string
from textual import work, on
from textual.app import App, ComposeResult
from textual.containers import VerticalScroll, HorizontalScroll, Container
from textual.widgets import Input, Markdown, Footer, Label



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

amisDICT_01 = load_amis_dictionary("dictionary/dict-amis.json")
amisDICT_02 = load_amis_dictionary("dictionary/dict-amis-safolu.json")
keySTR_amis01 = "\n".join([k for k in amisDICT_01])
keySTR_amis02 = "\n".join([k for k in amisDICT_02])
keySTR_amis = keySTR_amis01 + keySTR_amis02

sirayaDICT_01 = load_siraya_dictionary("dictionary/dict.jenny.json")
sirayaDICT_02 = load_siraya_dictionary("dictionary/dict.jenny2.json")
keySTR_siraya01 = "\n".join([k for k in sirayaDICT_01])
keySTR_siraya02 = "\n".join([k for k in sirayaDICT_02])
keySTR_siraya = keySTR_siraya01 + keySTR_siraya02

def MatchingQuery(queryLIST, dictSTR="amis") -> list:
    resultLIST = []
    if dictSTR == "amis":
        for q in queryLIST:
            if q in amisDICT_01:
                for content in amisDICT_01[q]["definitions"]:
                    resultLIST.append("## Definition: \n")
                    resultLIST.append(content["def"])
                    resultLIST.append("## Synonyms: \n")
                    resultLIST.append("\n".join(map(lambda s: "- "+s, content["synonyms"])))
                    resultLIST.append("\n============")
            if q in amisDICT_02:
                for content in amisDICT_02[q]["definitions"]:
                    resultLIST.append("## Definition: \n")
                    resultLIST.append(content["def"])
                    resultLIST.append("## Synonyms: \n")
                    resultLIST.append("\n".join(map(lambda s: "- "+s, content["synonyms"])))
                    resultLIST.append("\n============")
    elif dictSTR == "siraya":
        for q in queryLIST:
            if q in sirayaDICT_01:
                resultLIST.append("## Definition: \n")
                resultLIST.append(sirayaDICT_01[q]["definitions"][0]["def"])
                resultLIST.append("## Synonyms: \n")
                resultLIST.append("\n".join(map(lambda s: "- "+s, sirayaDICT_01[q]["definitions"][0]["synonyms"])))
                resultLIST.append("\n============")
            if q in sirayaDICT_02:
                resultLIST.append("## Definition: \n")
                resultLIST.append(sirayaDICT_02[q]["definitions"][0]["def"])
                resultLIST.append("## Synonyms: \n")
                resultLIST.append("\n".join(map(lambda s: "- "+s, sirayaDICT_02[q]["definitions"][0]["synonyms"])))
                resultLIST.append("\n============")
    return resultLIST

def FuzzyQuery(word, dictSTR="amis") -> list:   #NCaN
    resultLIST = []
    patternDICT = {"C":"[bcdfghjklmnpqrstvxz]",
                   "V":"[aeiuowyj]",
                   "N":"(?:ng|[mn])",
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
    if dictSTR == "amis":
        matches_amis = queryPat.findall(keySTR_amis)
        matches_amis = set(sorted(matches_amis))
        if matches_amis:
            for k in matches_amis:
                if k in amisDICT_01:
                    for content in amisDICT_01[k]["definitions"]:
                        resultLIST.append(f"## Match Entry: {k} \n")
                        resultLIST.append("## Definition: \n")
                        resultLIST.append(content["def"])
                        resultLIST.append("## Synonyms: \n")
                        resultLIST.append("\n".join(map(lambda s: "- "+s, content["synonyms"])))
                        resultLIST.append("\n============")
                if k in amisDICT_02:
                    for content in amisDICT_02[k]["definitions"]:
                        resultLIST.append(f"## Match Entry: {k} \n")
                        resultLIST.append("## Definition: \n")
                        resultLIST.append(content["def"])
                        resultLIST.append("## Synonyms: \n")
                        resultLIST.append("\n".join(map(lambda s: "- "+s, content["synonyms"])))
                        resultLIST.append("\n============")

    elif dictSTR == "siraya":
        matches_siraya = queryPat.findall(keySTR_siraya)
        matches_siraya = set(sorted(matches_siraya))
        if matches_siraya:
            for k in matches_siraya:
                if k in sirayaDICT_01:
                    resultLIST.append(f"## Match Entry: {k} \n")
                    resultLIST.append("## Definition: \n")
                    resultLIST.append(sirayaDICT_01[k]["definitions"][0]["def"])
                    resultLIST.append("## Synonyms: \n")
                    resultLIST.append("\n".join(map(lambda s: "- "+s, sirayaDICT_01[k]["definitions"][0]["synonyms"])))
                    resultLIST.append("\n============")
                if k in sirayaDICT_02:
                    resultLIST.append(f"## Match Entry: {k} \n")
                    resultLIST.append("## Definition: \n")
                    resultLIST.append(sirayaDICT_02[k]["definitions"][0]["def"])
                    resultLIST.append("## Synonyms: \n")
                    resultLIST.append("\n".join(map(lambda s: "- "+s, sirayaDICT_02[k]["definitions"][0]["synonyms"])))
                    resultLIST.append("\n============")
    return resultLIST

def PartialQuery(word, dictSTR="amis") -> list:  #?kaNCa?
    resultLIST = []
    #logger.debug(word)
    queryLIST = []
    patternDICT = {"C":"[bcdfghjklmnpqrstvxz]",
                   "V":"[aeiuowyj]",
                   "N":"(?:ng|[mn])",
                   "L":"[rl]",
                   "B":"[bpdtkg]"
                   }
    if not set("CVNLB").intersection(word):
        for char in word:
            if char == "?":
                queryLIST.append("[a-z]+")
            else:
                queryLIST.append(char)
    else:
        for char in word:
            logger.debug(char)
            if char == "?":
                queryLIST.append("[a-z]+")
            elif char in patternDICT:
                queryLIST.append(patternDICT[char])  #["[bpdtkg]"]
            else:
                queryLIST.append(char)               #["[bpdtkg]", "o", "b"]
    #logger.debug("queryLIST:{}".format(queryLIST))

    querySTR = "".join(queryLIST)
    queryPat = re.compile(querySTR)
    if dictSTR == "amis":
        #matches_amis = set([q.group(0) for q in queryPat.findall(keySTR_amis)]) #queryPat.findall(k) != []:
        matches_amis = queryPat.findall(keySTR_amis)
        matches_amis = set(sorted(matches_amis))

        #matches_amis02 = set([q.group(0) for q in queryPat.finditer(keySTR_amis02)]) #queryPat.findall(k) != []:
        #matches_amis02 = sorted(matches_amis02)
        if matches_amis:
            for k in matches_amis:
                if k in amisDICT_01:
                    for content in amisDICT_01[k]["definitions"]:
                        resultLIST.append(f"## Match Entry: {k} \n")
                        resultLIST.append("## Definition: \n")
                        resultLIST.append(content["def"])
                        resultLIST.append("## Synonyms: \n")
                        resultLIST.append("\n".join(map(lambda s: "- "+s, content["synonyms"])))
                        resultLIST.append("\n============")
                if k in amisDICT_02:
                    for content in amisDICT_02[k]["definitions"]:
                        resultLIST.append(f"## Match Entry: {k} \n")
                        resultLIST.append("## Definition: \n")
                        resultLIST.append(content["def"])
                        resultLIST.append("## Synonyms: \n")
                        resultLIST.append("\n".join(map(lambda s: "- "+s, content["synonyms"])))
                        resultLIST.append("\n============")

    elif dictSTR == "siraya":
        #matches_siraya = set([q.group(0) for q in queryPat.finditer(keySTR_siraya)]) #queryPat.findall(k) != []:
        matches_siraya = queryPat.findall(keySTR_siraya)
        matches_siraya = set(sorted(matches_siraya))

        #matches_siraya02 = set([q.group(0) for q in queryPat.finditer(keySTR_siraya02)]) #queryPat.findall(k) != []:
        #matches_siraya02 = sorted(matches_siraya02)
        if matches_siraya:
            for k in matches_siraya:
                if k in sirayaDICT_01:
                    resultLIST.append(f"## Match Entry: {k} \n")
                    resultLIST.append("## Definition: \n")
                    resultLIST.append(sirayaDICT_01[k]["definitions"][0]["def"])
                    resultLIST.append("## Synonyms: \n")
                    resultLIST.append("\n".join(map(lambda s: "- "+s, sirayaDICT_01[k]["definitions"][0]["synonyms"])))
                    resultLIST.append("\n============")
                if k in sirayaDICT_02:
                    resultLIST.append(f"## Match Entry: {k} \n")
                    resultLIST.append("## Definition: \n")
                    resultLIST.append(sirayaDICT_02[k]["definitions"][0]["def"])
                    resultLIST.append("## Synonyms: \n")
                    resultLIST.append("\n".join(map(lambda s: "- "+s, sirayaDICT_02[k]["definitions"][0]["synonyms"])))
                    resultLIST.append("\n============")
    return resultLIST

class DictionaryApp(App):
    """Searches a dictionary API as-you-type."""

    #CSS_PATH = "css/dictionary.tcss"
    CSS = """Screen {
    background: $panel;
}

Input {
    dock: top;
    margin: 1 0;
}

#head-container {
    background: $background 50%;
    margin: 0 0 0 0;

    border: tall $background;
    height: 1;
}
.head {
    width: 50%;
    border: solid red;

}

#amis-results {
    width: 100%;
    height: 100%;
    border: solid red;
}

#siraya-results {
    width: 100%;
    height: 100%;
    border: solid red;
}

#results-container {
    background: $background 50%;
    margin: 0 0 1 0;
    height: 100%;
    overflow: hidden auto;
    border: tall $background;
}


#results-container:focus {
    border: tall $accent;
}"""
    BINDINGS = [
        ("ctrl+q", "quit", "Quit"),
    ]
    def compose(self) -> ComposeResult:
        # <Need more work here>
        yield Input(placeholder="Look up a word, then press [Enter]!")
        #with HorizontalScroll(id="head-container"):
            #with Container(classes="head"):
                #yield Markdown("Amis Dictionary")
            #with Container(classes="head"):
                #yield Markdown("Siraya Dictionary")
        # </Need more work here>

        with HorizontalScroll(id="results-container"):
            with VerticalScroll(classes="scroll"):
                yield Markdown(id="amis-results")
            with VerticalScroll(classes="scroll"):
                yield Markdown(id="siraya-results")
        yield Footer()

    @on(Input.Submitted)
    async def on_input_changed(self) -> None:
        """A coroutine to handle a text changed message."""
        input = self.query_one(Input)
        word = input.value
        if word:
            self.lookup_dictionary(word)
        else:
            # Clear the results
            await self.query_one("#amis-results", Markdown).update("")
            await self.query_one("#siraya-results", Markdown).update("")

    # #Do our look-up here!   .*kan.*
    @work(exclusive=True)
    async def lookup_dictionary(self, word: str) -> None:  #if "[" "]" "_" "CVN" => string ; => regex

        resultLIST = []
        #logger.debug(word)
        resultLIST.append("# Amis Dictionary")
        if set("CVNLB").intersection(word) and "?" not in word:
            resultLIST.extend(FuzzyQuery(word, dictSTR="amis"))
        elif "?" in word:
            resultLIST.extend(PartialQuery(word, dictSTR="amis"))
        else:
            resultLIST.extend(MatchingQuery([word], dictSTR="amis"))
        self.query_one("#amis-results", Markdown).update("\n".join(resultLIST))

        resultLIST = []
        resultLIST.append("# Siraya Dictionary #")
        if set("CVNLB").intersection(word) and "?" not in word:
            resultLIST.extend(FuzzyQuery(word, dictSTR="siraya"))
        elif "?" in word:
            resultLIST.extend(PartialQuery(word, dictSTR="siraya"))
        else:
            resultLIST.extend(MatchingQuery([word], dictSTR="siraya"))

        self.query_one("#siraya-results", Markdown).update("\n".join(resultLIST))


    #@work(exclusive=True)
    #async def lookup_word(self, word: str) -> None:
        #"""Looks up a word."""
        #url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"

        #async with httpx.AsyncClient() as client:
            #response = await client.get(url)
            #try:
                #results = response.json()
            #except Exception:
                #self.query_one("#results", Markdown).update(response.text)
                #return

        #if word == self.query_one(Input).value:
            #markdown = self.make_word_markdown(results)
            #self.query_one("#results", Markdown).update(markdown)

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
    app = DictionaryApp()
    app.run()
    #word = "vuV?"
    #result = PartialQuery(word, dictSTR="siraya")
    #print(result)