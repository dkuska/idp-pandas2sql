import autoflake

from .NodeSelector import input_modules

src = """
import pandas

con = "sqlite:///test.db"

df1 = pandas.read_sql("SELECT attribute1 FROM table1", con)

result = pandas.read_sql("SELECT AVG(attribute1) AS avg_attribute1 FROM table1", con)
return result

"""


def delete_unused_variables(code: str) -> str:
    def pre_process(src: str) -> str:
        return "def some_function():\n" + src.replace("\n", "\n\t")

    def post_process(src: str) -> str:
        return src.replace("def some_function():\n", "").replace("\n\t", "\n")

    code = pre_process(code)
    module_names = ",".join([module.module_name for module in input_modules])
    new_code = autoflake.fix_code(
        code, additional_imports=module_names, remove_unused_variables=True, remove_rhs_for_unused_variables=True
    )
    return post_process(new_code)


def main():
    print(delete_unused_variables(src))


if __name__ == "__main__":
    main()
