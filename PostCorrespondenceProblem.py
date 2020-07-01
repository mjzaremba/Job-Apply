import json
import time

#Funkcja użyta do mierzenia czasu wykonywania danej metody(bruteforce, hillclimbing, tabu)
def measure_time(function):
    start = time.perf_counter()
    function()
    end = time.perf_counter()
    print(function.__name__, "took:", end-start, "s")

##Funkcje służące do odświerzenia naszego jsona
def refresh_working_json():
    global working
    working = json.load(open("working.json", 'r'))

def clear_working_json():
    global working
    clearJson = {"workingBlocks": ["", ""], "blocksAdded": [], "checkpoint": [], "sequence": ""}
    with open("working.json", 'w') as changeWorkingJson:
        json.dump(clearJson, changeWorkingJson)
    refresh_working_json()

#Funkcje używane dla metody Bruteforce:
def block_value(first, second):
    value = 0
    for i in range(0, min(len(first), len(second))):
        if first[i] != second[i]:
            value = value + 1
    return value

##"Brute force can be applied only if the number of dominoes we are going to use, is finite." - stackexchange
def best_block_to_add_with_limit(maxOccurs = 22):
    howMuchBestBlocks = 0
    ###pobieramy aktualny stan bloczków
    baseBlock = working.get("workingBlocks")

    ###pobieramy nowy bloczek do dodania
    for toCheck in range(1,5):
        numberOfOccurs = 0
        checkedBlock = data.get(str(toCheck))
        firstsqnc = baseBlock[0] + checkedBlock[0]
        secondsqnc = baseBlock[1] + checkedBlock[1]
        checkedBlockValue = block_value(firstsqnc, secondsqnc)
        newSequence = working.get("sequence") + str(toCheck)
        ###sprawdzamy ile razy nowy bloczek został użyty(limit)
        for a in newSequence:
            if a == str(toCheck):
                numberOfOccurs += 1
        if numberOfOccurs > maxOccurs:
            continue
        if checkedBlockValue == 0:
            howMuchBestBlocks += 1
            if howMuchBestBlocks > 1:
                add_checkpoint(newSequence)
            else:
                bestPair = toCheck
    if howMuchBestBlocks == 0:
            return 0
    ###zwracamy najlepszy możliwy bloczek do dodania
    return bestPair

def add_next_block(whichBlock):
        ###tworzymy chwilowy json którego zmienimy i zastapimy nim json working
    changedJson = json.load(open("working.json", 'r'))
    blockToAdd = data.get(str(whichBlock))
    baseBlock = working.get("workingBlocks")
    blocksUsed = working.get("blocksAdded")
        ###dodanie nowego bloczka do całego jsona working
    baseBlockFirst = baseBlock[0] + blockToAdd[0]
    baseBlockSecond = baseBlock[1] + blockToAdd[1]
    baseSequence = working.get("sequence") + str(whichBlock)
        ###sprawdzenie czy wszystkie bloczki zostały użyte
    if whichBlock not in blocksUsed:
        blocksUsed.append(whichBlock)
        ###tworzenie zmienionego jsona
    changedJson["workingBlocks"] = [baseBlockFirst, baseBlockSecond]
    changedJson["blocksAdded"] = blocksUsed
    changedJson["sequence"] = baseSequence
        ###dump do jsona working
    with open("working.json", 'w') as changeWorkingJson:
        json.dump(changedJson, changeWorkingJson)
    refresh_working_json()

##dodanie możliwośći powrotu gdy program nie będzie mógł kontynuować
def add_checkpoint(checkpointSequence):
    changedJson = json.load(open("working.json", 'r'))
    changedJson["checkpoint"].append(checkpointSequence)
    with open("working.json", 'w') as changeWorkingJson:
        json.dump(changedJson, changeWorkingJson)
    refresh_working_json()

def go_to_last_checkpoint():
    changedJson = json.load(open("working.json", 'r'))
    checkpoints = changedJson["checkpoint"]
    lastCheckpoint = checkpoints.pop(0)
    reversedBlockFirst = ""
    reversedBlockSecond = ""
    for i in lastCheckpoint:
        block = data.get(str(i))
        reversedBlockFirst += block[0]
        reversedBlockSecond += block[1]
    ###zmiana listy użytych bloczków dla nowego checkpointu
    newBlocksAdded = []
    for i in changedJson.get("sequence"):
        if int(i) not in newBlocksAdded:
            newBlocksAdded.append(int(i))

    changedJson["workingBlocks"][0] = reversedBlockFirst
    changedJson["workingBlocks"][1] = reversedBlockSecond
    changedJson["blocksAdded"] = newBlocksAdded
    changedJson["checkpoint"] = checkpoints
    changedJson["sequence"] = lastCheckpoint

    with open("working.json", 'w') as changeWorkingJson:
        json.dump(changedJson, changeWorkingJson)
    refresh_working_json()

##Bruteforce:
def Bruteforce(limit = 3):
    clear_working_json()
    for i in range(0,20000):
        if working["workingBlocks"][0] == working["workingBlocks"][1] and i > 0 and len(working["blocksAdded"]) == 4:
            print("solution found on iteration: ", i)
            break
        added = best_block_to_add_with_limit(limit)
        if added == 0:
            go_to_last_checkpoint()
            continue
        add_next_block(added)
    print("Brute Force found:")
    print(working["sequence"])

#Funkcje używane dla metody hillclimbing
import random

##Generowanie pseudo-przypadkowego rozwiązania od którego możemy zacząć
def generate_random_sol(limit, howBig = 5):
    randomSolution = ""
    exclude = []
    class StopLookingForThings(Exception): pass

    while(len(randomSolution) < howBig):
        try:
            randomBlock = str(random.choice([i for i in range(1,5) if i not in exclude]))
            occurs = 0
            for i in randomSolution:
                if randomBlock in i:
                    occurs += 1
                if occurs >= limit:
                    if randomBlock not in exclude:
                        exclude.append(randomBlock)
                    raise StopLookingForThings()
            randomSolution += randomBlock
        except StopLookingForThings:
            pass
    return randomSolution

##zmiana jsona working dla aktualnego rozwiązania
def update_working_json(solution):
    changedJson = json.load(open("working.json", 'r'))
    reversedBlockFirst = ""
    reversedBlockSecond = ""
    for i in solution:
        block = data.get(str(i))
        reversedBlockFirst += block[0]
        reversedBlockSecond += block[1]
    newBlocksAdded = []
    for i in solution:
        if int(i) not in newBlocksAdded:
            newBlocksAdded.append(int(i))
    changedJson["workingBlocks"][0] = reversedBlockFirst
    changedJson["workingBlocks"][1] = reversedBlockSecond
    changedJson["blocksAdded"] = newBlocksAdded
    changedJson["sequence"] = solution

    with open("working.json", 'w') as changeWorkingJson:
        json.dump(changedJson, changeWorkingJson)
    refresh_working_json()

##Generowanie solucji bliskich dla aktualnego rozwiązania
def generate_neighbours(howManyNeighbours = 84):
    neighbours = []
    refresh_working_json()
    centerOfAttention = working.get("sequence")
    baseBlocks = centerOfAttention[:-2] ###wszystko oprócz 2 ostatnich
    while(len(neighbours) < howManyNeighbours):
        for i in range(1, 5):
            newNeighbour = baseBlocks + str(i)
            neighbours.append(newNeighbour)
            for j in range(1, 5):
                newNeighbour = baseBlocks + str(i) + str(j)
                neighbours.append(newNeighbour)
                for k in range(1, 5):
                    newNeighbour = baseBlocks + str(i) + str(j) + str(k)
                    neighbours.append(newNeighbour)
    ###Zwracamy array
    return neighbours

##Generowanie solucji bliskich dla aktualnego rozwiązania - new approach -> better
def generate_neighbours_test():
    neighbours = []
    refresh_working_json()
    centerOfAttention = working.get("sequence")
    if len(centerOfAttention)>1:
        baseBlocks = centerOfAttention[:-2]
        for i in range(1, 5):
            newNeighbour = baseBlocks + str(i)
            neighbours.append(newNeighbour)
            newNeighbour = centerOfAttention + str(i)
            neighbours.append(newNeighbour)
    else:
        for i in range(1, 5):
            newNeighbour = str(i)
            neighbours.append(newNeighbour)
            for j in range(1, 5):
                newNeighbour = str(i) + str(j)
                neighbours.append(newNeighbour)
    return neighbours

def organize_neighbours(neighbours, limit):
    class StopLookingForThings(Exception): pass
    try:
        for neighbour in neighbours:
            for i in range(1, 5):
                occurs = 0
                for j in neighbour:
                    if str(i) in j:
                        occurs += 1
                if occurs >= limit:
                    neighbours.remove(neighbour)
                    raise StopLookingForThings()
    except StopLookingForThings:
        pass
    return neighbours

#liczenie wartości rozwiązania
def check_value_for_hc(sequence):
    blockFirst = ""
    blockSecond = ""
    for i in sequence:
        block = data.get(str(i))
        blockFirst += block[0]
        blockSecond += block[1]
    value = 0
    for i in range(0, min(len(blockFirst), len(blockSecond))):
        if blockFirst[i] != blockSecond[i]:
            value = value + 1
    value += (max(len(blockFirst), len(blockSecond)) - min(len(blockFirst), len(blockSecond)))
    if value == 0:
        blocksUsed = 0
        for j in range(1, 5):
            if str(j) in sequence:
                blocksUsed += 1
        if blocksUsed == 4 and len(blockFirst) == len(blockSecond):
            return 666
        else:
            return 0
    return value
        
def get_random_neighbour(neighbours):
    return neighbours[random.randint(0, len(neighbours) - 1)]

def get_close_neighbours(center, neighbours):
    #print("center: ", center)
    #print(neighbours)
    index = neighbours.index(center)
    refresh_working_json()
    excludedNeighbours = working.get("checkpoint")
    closeNeighbours = list()
    for i in range(-2, 3):
        closeNeighbour = neighbours[index + i]
        if closeNeighbour not in excludedNeighbours:
            closeNeighbours.append(closeNeighbour)
    return closeNeighbours


#Hill climbing
def hill_climbing(depth = 10000, blockLimit = 3):
    clear_working_json()
    bestSolution = generate_random_sol(blockLimit)
    update_working_json(bestSolution)
    bestValue = check_value_for_hc(bestSolution)
    for i in range(0, depth):
        neighbours = generate_neighbours()
        neighbours = organize_neighbours(neighbours, blockLimit)
        for neighbour in neighbours:
            neighbourValue = check_value_for_hc(neighbour)
            if neighbourValue == 666:
                print("solution found on iteration:", i)
                print("Hill climbing found:")
                print(neighbour)
                return neighbour
            elif neighbourValue <= bestValue:
                bestSolution = neighbour
                bestValue = neighbourValue
            ###Hill climbing gdy nie znajdzie rozwiązania powinien się zakończyć, ale w celach testowych zrobiłem, żeby się restartował i próbował dalej
            else:
                bestSolution = generate_random_sol(blockLimit)
                bestValue = check_value_for_hc(bestSolution)
                update_working_json(bestSolution)
        update_working_json(bestSolution)
    print("Hill climbing failed to find solution. Best solution:", bestSolution)
    return bestSolution

#Hill climbing z pseudo-przypadkowym wybieraniem sąsiada spośród listy 
def hill_climbing_nd(depth = 10000, blockLimit = 3):
    clear_working_json()
    bestSolution = generate_random_sol(blockLimit)
    update_working_json(bestSolution)
    bestValue = check_value_for_hc(bestSolution)
    for i in range(0, depth):
        neighbours = generate_neighbours()
        neighbours = organize_neighbours(neighbours, blockLimit)
        neighbour = get_random_neighbour(neighbours)
        neighbourValue = check_value_for_hc(neighbour)
        if neighbourValue == 666:
            print("solution found on iteration:", i)
            print("Hill climbing nd found:")
            print(neighbour)
            return neighbour
        elif neighbourValue <= bestValue:
            bestSolution = neighbour
            bestValue = neighbourValue
        else:
            bestSolution = generate_random_sol(blockLimit)
            bestValue = check_value_for_hc(bestSolution)
            update_working_json(bestSolution)
    print("Hill climbing nd failed to find solution. Best solution:", bestSolution)
    return bestSolution

#Tabu
def tabu(depth = 100):
    clear_working_json()
    sequence = generate_random_sol(3)
    add_checkpoint(sequence)
    for i in range(0, depth):
        startValue = check_value_for_hc(sequence)
        update_working_json(sequence)
        closeNeighbours = generate_neighbours_test()
        nv = []
        for neighbour in closeNeighbours:
            neighbourValue = check_value_for_hc(neighbour)
            nv.append(neighbourValue)
            if neighbourValue == 0:
                print("Tabu found:", neighbour)
                return
            if neighbourValue < startValue:
                print("nv:", neighbourValue, "cv:", startValue)
                startValue = neighbourValue
                sequence = neighbour
                update_working_json(sequence)
                add_checkpoint(sequence)
                break
    print(sequence)
    print(closeNeighbours)
    print(nv)
    print(startValue)
    return

#Wywołanie:
clear_working_json()
data = json.load(open("testEasy.json", 'r'))
working = json.load(open("working.json", 'r'))
print("Solution for our PCP problem:")
print(data["sol"])
measure_time(Bruteforce)
measure_time(hill_climbing)
measure_time(hill_climbing_nd)
measure_time(tabu)