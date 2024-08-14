import re
from rich.console import Console
from typing import Any, Callable, List, Literal
from yaml import load as y_load, BaseLoader
import json

console = Console()
print = console.print
print_json = lambda _json: console.print_json(json.dumps(_json))


def c_bool(x: str) -> bool:
    if x.lower() in ["true", "1", "t",]:
        return True
    else:
        return False


class Command:
    def __init__(self, function: Callable) -> None:
        self.function = function
        self.name = function.__name__
    
class CommandReader:
    def __init__(self, commands: List[Command], detail_path: str) -> None:
        self.commands = {
            command_object.name: command_object for command_object in commands
        }
        self.interpret_detail_file(detail_path)
    
    def convert_type(self, command_name: str, command_args: List[str]) -> List[Any]:
        args_type_fixed = []
        needed_arg_list = self.help_details[command_name]["usage"].split(" ")[1:]
        print(needed_arg_list)

        for index, arg in enumerate(needed_arg_list):
            arg_needed = re.match(r"(\<)[a-zA-Z_-]+:[a-zA-Z_-]+(\>)", arg)
            arg_optional = re.match(r"(\[)[a-zA-Z_-]+:[a-zA-Z_-]+(\])", arg)
            print(arg_needed)
            print(arg_optional)

            arg_needed = arg_needed.group()[1:-1].split(":") if arg_needed != None else None
            arg_optional = arg_optional.group()[1:-1].split(":") if arg_optional != None else None
            print(arg_needed)
            print(arg_optional)

            if arg_needed != None:
                arg_name = arg_needed[0]
                arg_value = command_args[index]
                arg_type = arg_needed[1]
                print(arg_type)
                
                type_command = str
                match arg_type:
                    case "int":
                        type_command = int
                    case "bool":
                        type_command = c_bool
                args_type_fixed.append(type_command(arg_value))
            elif arg_optional != None:
                arg_name = arg_optional[0]
                try:
                    arg_value = command_args[index]
                except IndexError:
                    continue
                arg_type = arg_optional[1]
                
                type_command = str
                match arg_type:
                    case "int":
                        type_command = int
                    case "bool":
                        type_command = c_bool
                args_type_fixed.append(type_command(arg_value))

        return args_type_fixed


    # def help(self): #TODO
    #     for command_name, command_data in self.details["commands"].items():
    #         command_description = command_data["description"]
    #         command_usage = command_data["usage"]

    def execute(self, command_name: str, args: List[str]) -> None:
        fixed_args = self.convert_type(command_name, args)
        print(fixed_args)
        output = self.commands[command_name].function(*fixed_args)
        if output != None:
            print(output)

    def prompt(self, styling: Literal["default"]="default") -> None:
        match styling:
            case "default":
                prompt = f"[bright_green]$[/bright_green] "
            case _:
                prompt = ""

        
        print(prompt, end="")
        _input = input()
        _input_split = _input.split()

        _input_command_name = _input_split[0]
        _input_command_args = _input_split[1:]

        self.execute(_input_command_name, _input_command_args)

    def interpret_detail_file(self, path: str):
        self.file = y_load(open(path), BaseLoader)
        self.help_details = self.file["commands"]
        #TODO Check against Schema TODO#

