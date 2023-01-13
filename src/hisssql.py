from argparse import ArgumentParser

from orchestrator import Orchestrator


def parse_file_contents(file_path: str) -> str:
    with open(file_path) as file:
        return file.read()


def write_new_file_contents(new_file_path: str, new_contents):
    with open(new_file_path, "w+") as file:
        file.writelines(new_contents)


def parse_args():
    parser = ArgumentParser(description="Optimize SQL based Pandas operations for Joins and Aggregations")
    parser.add_argument("filepath", type=str, help="Path to the file you want to translate")
    # TODO: Implement these
    parser.add_argument(
        "--inplace", type=bool, default=False, help="Whether or not to replace the file contents inplace or "
    )
    parser.add_argument("--new-filepath", type=str, help="Path of new file if --inplace==False")
    args = parser.parse_args()
    return args


def main():
    args = parse_args()
    src = parse_file_contents(args.filepath)
    print("Old Source:")  # DEBUG
    print(src)

    new_src = Orchestrator.transform(src)

    print("New Source:")  # DEBUG
    print(new_src)
    if args.inplace:
        new_file_path = args.filepath
    elif args.new_filepath:
        new_file_path = args.new_filepath
    else:
        new_file_path = f"optimized_{args.filepath}"

    write_new_file_contents(new_file_path, new_src)


if __name__ == "__main__":
    main()
