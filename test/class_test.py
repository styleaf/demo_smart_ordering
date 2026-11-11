from attrs import setters


class Animal:
    name:str
    age:int
    def __init__(self,name,age):
        self.name = name
        self.age = age
    def yell(self):
        print(f"{self.name}正在叫")


class Dog(Animal):
    species:str
    def __init__(self,species,name,age):
        self.species = species
        super().__init__(name,age)
    def yell(self):
        print("狗在叫")

father = Animal("dog",5)
son = Dog("jingmao","xiaom",2)
print()

class B:
    name:str
    def __init__(self,name):
        self._name = name

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self,name):
        self._name = name