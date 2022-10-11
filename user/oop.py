class Human():
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def hasBirthday(self):
        newAge = self.age + 1
        self.age = newAge
        return self.age

    
stefan = Human('stefanB', 30)

stefan.hasBirthday()
print (stefan.age)

