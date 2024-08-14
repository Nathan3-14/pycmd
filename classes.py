import re
from rich.console import Console
from typing import Any, Callable, Dict, List, Literal
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

    
class CommandReader:
    def __init__(self, commands: List[Callable], detail_path: str) -> None:
        self.commands = {
            command_function.__name__: command_function for command_function in commands
        }
        self.commands["help"] = self.help
        self.interpret_detail_file(detail_path)
        self.help_details["help"] = {
            "usage": "help \[command:str]", # type: ignore
            "description": "Provides help for all or a specific command(s)"
        }
    
    def convert_type(self, command_name: str, command_args: List[str]) -> List[Any]:
        args_type_fixed = []
        needed_arg_list = self.help_details[command_name]["usage"].split(" ")[1:]

        for index, arg in enumerate(needed_arg_list):
            arg_needed = re.match(r"(\<)[a-zA-Z_-]+:[a-zA-Z_-]+(\>)", arg)
            arg_optional = re.match(r"(\[)[a-zA-Z_-]+:[a-zA-Z_-]+(\])", arg)

            arg_needed = arg_needed.group()[1:-1].split(":") if arg_needed != None else None
            arg_optional = arg_optional.group()[1:-1].split(":") if arg_optional != None else None

            if arg_needed != None:
                arg_value = command_args[index]
                arg_type = arg_needed[1]
                
                type_command = str
                match arg_type:
                    case "int":
                        type_command = int
                    case "bool":
                        type_command = c_bool
                args_type_fixed.append(type_command(arg_value))
            elif arg_optional != None:
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

    def help_command(self, command_name: str) -> str:
        command_data = self.help_details[command_name]
        command_usage = command_data["usage"]
        command_description = command_data["description"]
        return f"[white bold]{command_name}:[/white bold]\n[magenta]\t{command_description}[/magenta]\n[magenta]\tUsage: [/magenta]{command_usage}"

    def help(self, command_name: str=""):
        if command_name != "":
            print(self.help_command(command_name))
        else:
            for command_name, _ in self.help_details.items():
                print(self.help_command(command_name))

    def execute(self, command_name: str, args: List[str]) -> None:
        fixed_args = self.convert_type(command_name, args)
        output = self.commands[command_name](*fixed_args)
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

