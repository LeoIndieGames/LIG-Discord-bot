class Vote:
    def __init__(self, name, message, choices):
        self.name = name
        self.message = message
        self.id = message.id
        self.choices = choices
        self.results = []
        for i in range(0, len(self.choices)):
            self.results.append(0)
        self.voters = []

    async def add_vote(self, author, choice):
        if author in self.voters:
            return False
        for i in range(0, len(self.choices)):
            if choice == self.choices[i]:
                self.results[i] += 1
                self.voters.append(author)
                return True
        return False

    def __str__(self) -> str:
        string = self.name + ": \n"
        for i in range(0, len(self.choices)):
            string += f"({self.results[i]}){self.choices[i]}"
            if i != (len(self.choices) - 1):
                string += "\t"
        return string