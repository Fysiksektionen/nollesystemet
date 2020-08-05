import csv
import json
import sys, getopt


def main(argv):
    inputfile = ''
    outputfile = ''
    try:
        opts, args = getopt.getopt(argv, "hi:o:", ["ifile=", "ofile="])
    except getopt.GetoptError:
        print('test.py -i <inputfile> -o <outputfile>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('test.py -i <inputfile> -o <outputfile>')
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inputfile = arg
        elif opt in ("-o", "--ofile"):
            outputfile = arg

    questions = []
    with open(inputfile, 'r') as infile:
        reader = csv.reader(infile)
        groups = next(reader)[2:]
        for i, row in enumerate(reader):
            questions.append(
                {
                    "question_type": "RADIO",
                    "number_label": row[0],
                    "title": row[1],
                    "answers": [
                        {
                            "value": answer,
                            "group": groups[group_num]
                        } for group_num, answer in enumerate(row[2:])
                    ]
                }
            )
            # print(questions[-1])

    json_out = {
        "dynamic_questions": questions
    }

    with open(outputfile, 'w') as outfile:
        json.dump(json_out, outfile)


if __name__ == "__main__":
    main(sys.argv[1:])