from __future__ import annotations

try:
    import httpx
except ImportError:
    raise ImportError("Please install httpx with 'pip install httpx' ")

import json
from textual import work
from textual.app import App, ComposeResult
from textual.containers import VerticalScroll
from textual.widgets import Input, Markdown


def load_dictionary(file_path: str) -> dict:
    data = json.load(open(file_path, encoding="utf-8"))
    return {f"{item['title']}": {
        "definitions": [
            {
                "synonyms": definition.get("synonyms", []),
                "def": definition.get("def", "").replace("￻", " ").replace("￹", " ").replace("￺", " ")
            }
            for definition in item["heteronyms"][0].get("definitions", [])
        ]
    }
    for item in data}
amisDICT_01 = load_dictionary("dictionary/dict-amis.json")
amisDICT_02 = load_dictionary("dictionary/dict-amis-safolu.json")
#amisDICT_03 = load_dictionary("dictionary/dict-concised.audio.json")
siraya_data = json.load(open("dictionary/dict.jenny.json", encoding="utf-8"))
sirayaDICT = {f"{item['title']}": {"definitions": item["heteronyms"][0].get("definitions", [])} for item in siraya_data}

class DictionaryApp(App):
    """Searches a dictionary API as-you-type."""

    CSS_PATH = "css/dictionary.tcss"

    def compose(self) -> ComposeResult:
        yield Input(placeholder="Search for a word")
        with VerticalScroll(id="results-container"):
            yield Markdown(id="results")

    async def on_input_changed(self, message: Input.Changed) -> None:
        """A coroutine to handle a text changed message."""
        if message.value:
            #self.lookup_word(message.value)
            self.lookup_dictionary(message.value)
        else:
            # Clear the results
            await self.query_one("#results", Markdown).update("")


# #Do our look-up here!   .*kan.*
    @work(exclusive=True)
    async def lookup_dictionary(self, word: str) -> None:  #if "[" "]" "_" "CVN" => string ; => regex
        resultLIST = []
        resultLIST.append("# Amis Dictionary")
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
        process_dictionary(word, amisDICT_01, resultLIST)
        process_dictionary(word, amisDICT_02, resultLIST)
        
        resultLIST.append("# Siraya Dictionary")
        if word in sirayaDICT:
            resultLIST.append("## Definition:")
            resultLIST.append(sirayaDICT[word]["definitions"][0]["def"])
            resultLIST.append("## Synonyms:")
            resultLIST.append("\n".join(sirayaDICT[word]["definitions"][0]["synonyms"]))
                       
        if word == self.query_one(Input).value:
            #markdown = self.make_word_markdown("\n".join(resultLIST))
            self.query_one("#results", Markdown).update("\n".join(resultLIST))


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
    app = DictionaryApp()
    app.run()
