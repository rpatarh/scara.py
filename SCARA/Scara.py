import sys
import uos
import machine
from math import sqrt, pi, atan2, acos, degrees

# Nama direktori dan file untuk menyimpan nilai-nilai
DIRECTORY = "SCARA"
DATA_DIRECTORY = DIRECTORY + "/DATA_TXT"
DATA_FILE = DATA_DIRECTORY + "/Scara_Plasma_Data.txt"

# Inisialisasi variabel global untuk menyimpan nilai
input_file = 'SCARA/DATA_GCODE/kotak.gcode'
output_file = 'SCARA/DATA_GCODE/kotak_polar_Plasma.gcode'
L1, L2 = 10, 10
min_segment = 1

# Inisialisasi variabel untuk menyimpan data awal sebelum diubah
initial_data = {
    "input_file": input_file,
    "output_file": output_file,
    "L1": L1,
    "L2": L2,
    "min_segment": min_segment
}

def ensure_directory(path):
    # Pastikan direktori ada
    try:
        uos.mkdir(path)
    except OSError:
        pass  # Direktori mungkin sudah ada

def ensure_directories():
    ensure_directory(DIRECTORY)
    ensure_directory(DATA_DIRECTORY)

def load_data():
    global input_file, output_file, L1, L2, min_segment
    ensure_directories()
    try:
        with open(DATA_FILE, "r") as file:
            lines = file.readlines()
            
            input_file  = lines[0].strip().split('=')[1].strip()
            output_file = lines[1].strip().split('=')[1].strip()
            
            L1          = float(lines[2].strip().split('=')[1].strip())
            L2          = float(lines[3].strip().split('=')[1].strip())
            min_segment = float(lines[4].strip().split('=')[1].strip())
            
    except OSError:
        save_data()  # Simpan data default jika file tidak ditemukan
        
    except (ValueError, IndexError):
        print("Error membaca data dari file, menggunakan nilai default.")
        save_data()  # Simpan data default jika ada kesalahan saat membaca file

def save_data():
    ensure_directories()
    with open(DATA_FILE, "w") as file:
        file.write(f"input_file = {input_file}\n")
        file.write(f"output_file = {output_file}\n")
        file.write(f"L1 = {L1}\n")
        file.write(f"L2 = {L2}\n")
        file.write(f"min_segment = {min_segment}\n")

def print_data():
    print("\nData :")
    print("------")
    print(f"    1. input_file              = {input_file}")
    print(f"    2. output_file             = {output_file}")
    print(f"    3. L1 (default 10)         = {L1}")
    print(f"    4. L2 (default 10)         = {L2}")
    print(f"    5. min_segment (default 1) = {min_segment}")

def print_menu():
    print("\nMenu Pilihan :")
    print("--------------")
    print("    1. Exit and Reboot")
    print("    2. Exit")
    print("    3. Edit Data")
    print("    4. Scara RH")
    print("    5. Scara LH")
    print("    6. Reset Data")

def edit_data():
    global input_file, output_file, L1, L2, min_segment
    
    while True:
        print_data()
        choice = input("\nPilih nomor ( 1 - 5 ) atau 'Enter' untuk kembali: ")
        
        if choice == '1':
            input_file = input(f"Masukkan nama input_file ({input_file}): ") or input_file
            
        elif choice == '2':
            output_file = input(f"Masukkan nama output_file ({output_file}): ") or output_file
            
        elif choice == '3':
            try:
                L1 = float(input(f"Masukkan nilai L1 ({L1}): ") or L1)
            except ValueError:
                print("Input tidak valid, pastikan Anda memasukkan angka.")
                
        elif choice == '4':
            try:
                L2 = float(input(f"Masukkan nilai L2 ({L2}): ") or L2)
            except ValueError:
                print("Input tidak valid, pastikan Anda memasukkan angka.")
                
        elif choice == '5':
            try:
                min_segment = float(input(f"Masukkan nilai min_segment ({min_segment}): ") or min_segment)
            except ValueError:
                print("Input tidak valid, pastikan Anda memasukkan angka.")
                
        else:
            print_data()
            break
        
        save_data()



def reset_data():
    global input_file, output_file, L1, L2, min_segment
    input_file  = initial_data["input_file"]
    output_file = initial_data["output_file"]
    L1          = initial_data["L1"]
    L2          = initial_data["L2"]
    min_segment = initial_data["min_segment"]
    save_data()
    print("Data telah direset ke nilai default.")


# ---------------------------------------------------------------
def SCARA_Right_Hand(x, y, L1, L2):
    R = sqrt(x**2 + y**2)
    if R > (L1 + L2):
        print('.......... Out of working area !!')
        return None, None
    alpha  = atan2(y, x)
    beta   = acos ( ( (L1**2)+(L2**2)-(R**2) ) / (2*L1*L2) )
    thetaA = degrees ( alpha - (pi-beta)/2 )
    thetaB = degrees (pi - beta)
    thetaA = round(thetaA, 4)
    thetaB = round(thetaB, 4)
    if y < 0 and x < 0:
        thetaA = 360 + thetaA
    return thetaA, thetaB

def SCARA_Left_Hand(x, y, L1, L2):
    R = sqrt(x**2 + y**2)
    if R > (L1 + L2):
        print('.......... Out of working area !!')
        return None, None
    alpha  = atan2(y, x)
    beta   = acos(((L1**2) + (L2**2) - (R**2)) / (2 * L1 * L2))
    thetaA = degrees(alpha + (pi - beta) / 2)
    thetaB = degrees(pi - beta)
    thetaA = round(thetaA, 4)
    thetaB = round(thetaB, 4)
    if y < 0 and x < 0:
        thetaA = 360 + thetaA
    return thetaA, thetaB



def segment_line(x0, y0, x1, y1, min_segment):
    segments = []
    dx = x1 - x0
    dy = y1 - y0
    
    distance = sqrt(dx**2 + dy**2)
    
    num_segments = max(int(distance / min_segment), 1)
    
    for i in range(num_segments + 1):
        x = x0 + i * dx / num_segments
        y = y0 + i * dy / num_segments
        segments.append((x, y))
    
    return segments

def read_gcode(input_file, output_file, L1, L2, min_segment):
    with open(input_file, 'r') as file, open(output_file, 'w') as outfile:
        outfile.write("; SCARA_Right_Hand\n")
        outfile.write("; X = theta1 \n")
        outfile.write("; Y = theta2 \n")        
        outfile.write("; ================\n\n")
        
        last_x, last_y = 0, 0  # Starting position assumed to be origin
        last_command = None
        last_Z = None
        
        for line in file:
            if line.startswith('G0') or line.startswith('G1'):
                parts = line.strip().split()
                
                command = parts[0]
                x = None
                y = None
                
                for part in parts:
                    if part.startswith('X'):
                        x = float(part[1:])
                    elif part.startswith('Y'):
                        y = float(part[1:])
                
                if x is not None and y is not None:
                    if command == 'G1' and last_command == 'G1':
                        segments = segment_line(last_x, last_y, x, y, min_segment)
                    else:
                        segments = [(x, y)]
                    
                    for seg_x, seg_y in segments:
                        thetaA, thetaB = SCARA_Right_Hand(seg_x, seg_y, L1, L2)
                        
                        if thetaA is not None and thetaB is not None:
                            if command == 'G0':
                                new_command = 'G0'
                                Z = 5
                            elif last_command == 'G0' and command == 'G1':
                                new_command = 'G0'
                                Z = 5
                            else:
                                new_command = 'G1'
                                Z = 0
                            
                            # Write Z value only once before G1 command
                            if Z != last_Z:
                                outfile.write(f"{new_command} Z{Z:.2f}\n")
                                print(f"{new_command} Z{Z:.2f}")
                            
                            outfile.write(f"{new_command} X{thetaA:.2f} Y{thetaB:.2f}\n")
                            print(f"{new_command} X{thetaA:.2f} Y{thetaB:.2f}")
                            
                            last_Z = Z

                    outfile.write("\n")
                    print('')

                    last_x, last_y = x, y  # Update last position
                    last_command = command

    Print_Text(L1, L2, input_file, output_file)
    
    

def Print_Text(L1, L2, input_file, output_file):
    print('\n==================')
    print('SCARA_Right_Hand :')
    print('==================\n')
    print('     L1, L2 = ', L1, ', ', L2, sep='')
    print('min_segment = ', min_segment, sep='')
    print('-------------------------------------------------------')    
    print('input_file  = ', input_file, sep='')
    print('output_file = ', output_file, sep='')
    print('-------------------------------------------------------\n')
    
    
# ---------------------------------------------------------------
def main_menu():
    load_data()
    print_data()
    
    while True:
        print_menu()
        choice = input("\nPilih opsi (1-6): ")
        
        if choice == '1':
            print("\nExit program.")
            machine.reset()
            
        elif choice == '2':
            #break  # Kembali ke step sebelumnya
            sys.exit()
        
        elif choice == '3':
            edit_data()
            
        elif choice == '4':
            print ('\nScara Right Hand')
            print ('----------------\n')
            
            read_gcode(input_file, output_file, L1, L2, min_segment)
            sys.exit()
            
        elif choice == '5':
            print ('\nScara Left Hand')
            #break
            #return
            sys.exit()
            
        elif choice == '6':
            reset_data()
            print_data()
            
        else:
            print("Pilihan tidak valid, coba lagi.")

def main():
    while True:
        main_menu()

if __name__ == "__main__":
    main()
