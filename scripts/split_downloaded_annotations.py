import argparse
from prodigy.components.db import connect
from table_ner.utils import read_jsonl
import os


def run(filename: str, save_local: bool):
    print(filename)
    annotations = list(read_jsonl(str(filename)))
    if not save_local:
        os.remove(filename)
    uq_annotators = set([x["_session_id"] for x in annotations])
    db = connect()
    dataset_names = []
    for annotator in uq_annotators:
        sub_annotations = [an for an in annotations if an["_session_id"] == annotator]
        if db.get_dataset(annotator):
            db.drop_dataset(annotator)
        annotator_dataset_name = annotator
        db.add_dataset(annotator_dataset_name)
        dataset_names.append(annotator_dataset_name)
        assert annotator_dataset_name in db  # check  dataset was added
        sub_annotations_out = [{k: v for k, v in d.items() if k != "_session_id"} for d in sub_annotations]
        db.add_examples(sub_annotations_out, [annotator])  # add examples to dataset
        dataset = db.get_dataset(annotator)  # retrieve a dataset
        print("=====", annotator.split("-")[-1], " made: ", len(dataset), " annotations ========")
    print("The new Prodigy Dataset names are: \n:", dataset_names)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--filename", type=str, help="Annotate file that we want to split",
                        default='table_ner_trial-output.jsonl'
                        )
    parser.add_argument("--save-local", type=bool, help="Whether to save the jsonl file locally",
                        default=False
                        )
    args = parser.parse_args()

    run(filename=args.filename, save_local=args.save_local)


if __name__ == '__main__':
    main()
