import sys

registers = {}
registers_new = {}
data_memory = {}
instructions = []
INB=[]
AIB=[]
LIB=[]
ADB=[]
REB=[]
step_count=0
while_cond=True

def write():
    global REB, registers_new
    if REB:
        smol_id = min(range(len(REB)), key=lambda i: REB[i]['id'])
        smol_element = REB.pop(smol_id)
        registers_new[smol_element['dest']] = smol_element['final_value']

def load():
    global ADB, REB, data_memory
    if ADB:
        element = ADB.pop(0)
        address_value = data_memory.get(str(element["final_address"]))
        element_new = {"dest": element["dest"], "final_value": address_value,"id":element["id"]}
        REB.append(element_new)

def addr():
    global ADB, LIB, registers
    if LIB:
        instruction = LIB.pop(0)
        final_address = instruction["src1"] + instruction["src2"]
        element = {"dest": instruction["dest"], "final_address": final_address,"id": instruction["id"]}
        ADB.append(element)

    
def issue2():
    global INB, LIB
    if INB:
        if INB[0]["opcode"] == "LD":
            LIB.append(INB.pop(0))

def alu():
    global AIB, REB
    if AIB:
        element = AIB.pop(0)
        
        opcode = element["opcode"]
        
        if opcode == "ADD":
            final_value = element["src1"] + element["src2"]
        elif opcode == "SUB":
            final_value = element["src1"] - element["src2"]
        elif opcode == "AND":
            final_value = element["src1"] & element["src2"]
        elif opcode == "OR":
            final_value = element["src1"] | element["src2"]
        else:
            final_value = None
        
        if final_value is not None:
            element_new = {"dest": element["dest"], "final_value": final_value, "id": element["id"]}
            REB.append(element_new) 



def issue1():
    global INB, AIB 
    if INB:
        if INB[0]["opcode"] in ["ADD", "SUB", "AND", "OR"]:
            AIB.append(INB.pop(0))

def decode():
    global registers, data_memory, instructions, INB, AIB, LIB, ADB, REB, step_count
    if instructions:
        instruction = instructions.pop(0)
        rs1, rs2 = read(instruction["src1"], instruction["src2"])
        instruction["src1"] = rs1
        instruction["src2"] = rs2
        INB.append(instruction)

def read(rs1, rs2):
    global registers, data_memory, instructions, INB, AIB, LIB, ADB, REB, step_count
    return registers.get(rs1), registers.get(rs2)


def check_while():
    global instructions, INB, AIB, LIB, ADB, REB, while_cond

    if not instructions and not INB and not AIB and not LIB and not ADB and not REB:
        while_cond = False
        print_output()
    else:
        while_cond = True


def print_output():
    global registers, data_memory, instructions, INB, AIB, LIB, ADB, REB, step_count

    with open('simulation.txt', 'a') as f:
        f.write(f"STEP {step_count}:\n")

        f.write("INM:")
        for instr in instructions[:-1]:
            f.write(f'<{instr["opcode"]},{instr["dest"]},{instr["src1"]},{instr["src2"]}>,')
        if instructions:
            f.write(f'<{instructions[-1]["opcode"]},{instructions[-1]["dest"]},{instructions[-1]["src1"]},{instructions[-1]["src2"]}>')
        f.write('\n')

        f.write("INB:")
        for instr in INB[:-1]:
            f.write(f'<{instr["opcode"]},{instr["dest"]},{instr["src1"]},{instr["src2"]}>,')
        if INB:
            f.write(f'<{INB[-1]["opcode"]},{INB[-1]["dest"]},{INB[-1]["src1"]},{INB[-1]["src2"]}>')
        f.write('\n')

        f.write("AIB:")
        for instr in AIB[:-1]:
            f.write(f'<{instr["opcode"]},{instr["dest"]},{instr["src1"]},{instr["src2"]}>,')
        if AIB:
            f.write(f'<{AIB[-1]["opcode"]},{AIB[-1]["dest"]},{AIB[-1]["src1"]},{AIB[-1]["src2"]}>')
        f.write('\n')

        f.write("LIB:")
        for instr in LIB[:-1]:
            f.write(f'<{instr["opcode"]},{instr["dest"]},{instr["src1"]},{instr["src2"]}>,')
        if LIB:
            f.write(f'<{LIB[-1]["opcode"]},{LIB[-1]["dest"]},{LIB[-1]["src1"]},{LIB[-1]["src2"]}>')
        f.write('\n')

        f.write("ADB:")
        for instr in ADB[:-1]:
            f.write(f'<{instr["dest"]},{instr["final_address"]}>,')
        if ADB:
            f.write(f'<{ADB[-1]["dest"]},{ADB[-1]["final_address"]}>')
        f.write('\n')

        f.write("REB:")
        for instr in REB[:-1]:
            f.write(f'<{instr["dest"]},{instr["final_value"]}>,')
        if REB:
            f.write(f'<{REB[-1]["dest"]},{REB[-1]["final_value"]}>')
        f.write('\n')

        f.write("RGF:")
        items = list(registers.items())  
        for reg, value in items[:-1]:  
            f.write(f'<{reg},{value}>,')
        if items:  
            f.write(f'<{items[-1][0]},{items[-1][1]}>')  
        f.write('\n')

        f.write("DAM:")
        items = list(data_memory.items())  
        for address, value in items[:-1]:  
            f.write(f'<{address},{value}>,')
        if items:  
            f.write(f'<{items[-1][0]},{items[-1][1]}>') 
        f.write('\n\n')




def simulate_psim():
    global step_count, registers_new, registers
    while while_cond:
        print_output()
        write()
        load()
        addr()
        issue2()
        alu()
        issue1()
        decode()
        registers = registers_new.copy()
        step_count+=1
        check_while()

def read_files():
    global registers, data_memory, instructions,registers_new

    try:
        with open('registers.txt', 'r') as file:
            for line in file:
                line = line.strip().replace('<', '').replace('>', '')
                parts = line.split(',')
                if len(parts) == 2:
                    registers[parts[0]] = int(parts[1])
            registers_new = registers.copy()
    except Exception as e:
        print(f"Error when trying to open the registers file: {e}")

    try:
        with open('datamemory.txt', 'r') as file:
            for line in file:
                line = line.strip().replace('<', '').replace('>', '')
                parts = line.split(',')
                if len(parts) == 2:
                    data_memory[parts[0]] = int(parts[1])
    except Exception as e:
        print(f"Error when trying to open the datamemory file: {e}")

    try:
        with open('instructions.txt', 'r') as file:
            count = 1
            for line in file:
                line = line.strip().replace('<', '').replace('>', '')
                parts = line.split(',')
                if len(parts) == 4:
                    instruction = {
                        'opcode': parts[0],
                        'dest': parts[1],
                        'src1': parts[2],
                        'src2': parts[3],
                        'id': count
                    }
                    instructions.append(instruction)
                    count += 1
    except Exception as e:
        print(f"Error when trying to open the instructions file: {e}")



def main():
    with open('simulation.txt', 'w') as f:
        f.close()
        pass
    read_files()
    simulate_psim()


if __name__ == "__main__":
    main()
