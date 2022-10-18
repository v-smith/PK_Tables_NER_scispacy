"""Convert entity annotation from character-level NER to spaCy v3 .spacy format."""
import warnings
import typer
from pathlib import Path
import spacy
from spacy.tokens import DocBin
from table_ner.utils import read_jsonl, character_annotations_to_spacy_doc, clean_spans, which_spans_join, \
    is_consecutive, join_spans
from table_ner.partial_split_tokenizer import create_tokenizer
from table_ner.whitespace_tokenizer import WhitespaceTokenizer


def convert(
        input_path: Path = typer.Option(default='../data/model_vs_annotator/PopDemCombined/model_compare_review_dev.jsonl'),
        output_path: Path = typer.Option(default='../data/spacy/dev_PopDemCombo.spacy/'),
        scispacy_base_tok: bool = typer.Option(default=False)
):
    if scispacy_base_tok:
        #nlp = spacy.load("en_core_sci_lg")
        a=1
    else:
        #nlp = spacy.load("/home/vsmith/anaconda3/lib/python3.9/site-packages/en_core_web_sm/en_core_web_sm-3.2.0")
        #nlp.tokenizer = nlp
        #nlp = spacy.blank("en")
        #nlp.tokenizer = WhitespaceTokenizer(nlp.vocab)
        nlp = spacy.blank("en")
        nlp.tokenizer = create_tokenizer(nlp)
    db = DocBin()

    misaligned_sentences = 0
    raw_annotations = list(read_jsonl(input_path))
    for annot_sentence in raw_annotations:
        spans = annot_sentence["spans"]
        text = annot_sentence["text"]
        if spans:
            join_indexes = which_spans_join(text=text, same_spans=spans)
            # check for consecutive indexes
            consec_indexes = is_consecutive(join_indexes)
            # combine consecutive entries from same spans
            final_spans = join_spans(join_indexes=join_indexes, consec_indexes=consec_indexes, same_spans=spans)
            cleaned_spans = clean_spans(text=text, spans=final_spans)
            annot_sentence.update({"spans": cleaned_spans})

        doc, misaligned = character_annotations_to_spacy_doc(inp_annotation=annot_sentence, tokenizer_model=nlp)
        if misaligned:
            misaligned_sentences += 1
        else:
            db.add(doc)

    output_path.parents[0].mkdir(parents=True, exist_ok=True)
    db.to_disk(output_path)
    if misaligned_sentences > 0:
        warnings.warn(f"Number of misaligned sentences: {misaligned_sentences}"
                      f"({round(misaligned_sentences*100 / len(raw_annotations), 2)}%)")


if __name__ == "__main__":
    typer.run(convert)
