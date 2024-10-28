import os.path




class CLI_session():
    def __init__(self,):
        self.running = True
        self.version = "0.0.1"
        self.implemented_commands = ("help","exit")
        self.main()
        
    def main(self) -> None:
        print(f"EmailSender CLI tool version {self.version}\nType help voor commands")
        while self.running:
            user_command = self.split_into_subcategories(input())
            
            match user_command["command"]:
                case "help" :

                    if "command" in user_command["params"]:
                        try:
                            print(self.get_command_description(user_command["command"]))
                        except FileNotFoundError:
                            print("could not find the command you are describing")
                    else:


                        print(f'''Syntax for CLI:
                        main_command -some_param=some_value -param=...
                              
                        to know more about a specific command type:
                        help -command="command_name"
                              
                        Availabe commands:
                        {"\n".join(self.implemented_commands)}
                        '''.replace("    ",""))
                case "exit":
                    print("Closing...")
                    self.running = False
    
    def split_into_subcategories(self,input_str:str) -> dict[str:str,str:any] | None:
        '''
        Takes a string and returns a dictionary which contains the following categories:
        "command": "some_command" (str)
        "params": {"param_name" : value, ...}
        '''
        all_params_and_values = {}
        parsed_str = input_str.replace(" ", "")

        split_str = parsed_str.split("-")
        
        main_command = split_str[0]
        if len(split_str) >1:
            try:
                params_and_values = [dict([p_and_val.split("=")]) for p_and_val in split_str[1:]]

            except ValueError:
                print('Syntax error: Ensure parameters are in the form -param=value')
                return None
            for d in params_and_values:
                all_params_and_values.update(d)
            #convert the value to int or float if necessary after removing the "" or '' 
            all_params_and_values = {param: self.check_conversion_to_int_or_float(value.replace('"',"").replace("'","")) for param,value in all_params_and_values.items()}

        return {"command":main_command,
                "params": all_params_and_values}
    
    def get_command_description(self,command_name):
        absolute_path = os.path.dirname(__file__)
        with open(f"{absolute_path}/command_descriptions/help_{command_name}.txt" ,"r") as help_command:
            return help_command.read()
        

    def check_conversion_to_int_or_float(self,value:str)-> str|int|float:
        '''
        Checks if the value can be converted to float or string
        returns: int | float if can be converted
        returns: str if cannot be converted
        '''
        
        try:
            if int(value) == float(value):
                return int(value)
            return float(value)

        except ValueError:
            return value
if __name__ == "__main__":

    CLI_session()


