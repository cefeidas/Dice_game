"""
This script implements a simplified version of the board game "Can't Stop"
for two players. The game is played using a Google Sheets worksheet as the
game board. The players take turns rolling dice, choosing combinations, and
moving their pieces on the board. The first player to reach a winning
coordinate is declared the winner.
"""

# Your code goes here
# You can delete these comments, but do not change the name of this file
# Write your code to expect a terminal of 80 characters wide and 24 rows high

import random
import itertools
import gspread

from google.oauth2.service_account import Credentials

SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
    ]

CREDS = Credentials.from_service_account_file('creds.json')
SCOPED_CREDS = CREDS.with_scopes(SCOPE)
GSPREAD_CLIENT = gspread.authorize(SCOPED_CREDS)
SHEET = GSPREAD_CLIENT.open('Can_t_Stop')
board = SHEET.worksheet('board')
data = board.get_all_values()


def clear_board():
    """
    Clears the board on the Google Sheet to prepare for a new game.
    The cells in the range from B3 to L14 are set to an empty string.
    """
    # Access the Google Sheet
    worksheet_to_clear = SHEET.worksheet('board')

    # Fetch the cell range
    cell_list = worksheet_to_clear.range('B3:L14')

    # Update each cell in the fetched range
    for cell in cell_list:
        cell.value = ''
    
    # Update the changed cells in batch
    worksheet_to_clear.update_cells(cell_list)

    print("Board cleared. All set for a new game!")


def presenting_the_game():
    """
    This function prints introductory sentences.
    That helps the players understand the game before it starts.
    """
    print("Welcome to Can't stop, a push your luck game.\n")
    print('This is a simplified version of the game.\n')
    print('If you are interested in the original rules,\n')
    print('visit: "https://www.ultraboardgames.com/cant-stop/game-rules.php\n')
    print('The rules for this project can be found in the README file.\n')
    print("Let's get started!")


def naming_the_players():
    """
    This function asks and stores the names of two players.
    """
    while True:  # Loop to keep asking for Player One's name until valid input is received
        player_one = input('Player one, please enter your name: \n')
        if len(player_one) > 20:
            print("Error: Name too long, it should be a maximum of 20 characters.")
        elif len(player_one.strip()) == 0:
            print("Error: Blank space is not a valid name.")
        else:
            break  # Exit loop if input is valid

    while True:  # Loop to keep asking for Player Two's name until valid input is received
        player_two = input('Player Two, please enter your name: \n')
        if len(player_two) > 20:
            print("Error: Name too long, it should be a maximum of 20 characters.")
        elif len(player_two.strip()) == 0:
            print("Error: Blank space is not a valid name.")
        else:
            break  # Exit loop if input is valid

    return [player_one, player_two]


def roll_dice():
    """
    This function rolls the four dice and returns the resulting numbers.
    """
    return [random.randint(1, 6) for i in range(4)]


def get_dice_combinations(numbers):
    """
    This function returns all the possible combinations
    of two dice from the rolled numbers.
    """
    return list(itertools.combinations(numbers, 2))


def get_valid_choice(target_number, dice_combinations, player):
    valid_sums = [sum(comb) for comb in dice_combinations]
    if target_number:
        if target_number[0] in valid_sums:
            print(f"Great {player}, your target number {target_number[0]} is valid for this round.")
            return target_number[0]
        else:
            print(f"Sorry {player}, your target number {target_number[0]} is not valid this round.")
            return None
    else:
        while True:
            try:
                dice_choice = int(input(f"""{player}, choose any two numbers and add them together.
                This will be your target number for the rest of the game: \n"""))
                if dice_choice in valid_sums:
                    return dice_choice
                else:
                    print(f"{dice_choice} is not a valid sum. Please try again.\n")
            except ValueError as error:
                print(f"Invalid data: {error}, please try again.\n")
                continue


def should_continue_rolling():
    """
    This function asks the player if they want to continue rolling the dice
    and returns True if they do, False otherwise.
    """
    while True:
        continue_rolling = input("Continue rolling the dice? Y/N: \n").upper()
        if continue_rolling == 'Y':
            return True
        elif continue_rolling == 'N':
            return False
        else:
            print("Invalid input. Please enter Y or N. \n")


def turn(target_number, player):
    original_target_number = target_number.copy()
    scored = False

    while True:
        numbers = roll_dice()
        print(f"{player}, you rolled the following numbers: {numbers}\n")
        dice_combinations = get_dice_combinations(numbers)
        dice_choice = get_valid_choice(target_number, dice_combinations, player)

        if dice_choice is None:
            return original_target_number, False
        elif not target_number:
            target_number = [dice_choice, 1]
            scored = True
        elif dice_choice == target_number[0]:
            target_number[1] += 1
            scored = True

        print(f'{player}, you chose the number {target_number[0]}\n')
        print(f'You moved up to the square {target_number[1]}.\n')

        if not should_continue_rolling():
            print(f"The result is: {target_number}\n")
            return target_number, scored


def update_sheet(coordinates, player, scored):
    """
    This function updates the worksheet.
    It uses the values returned from the turn() function.
    """
    if not coordinates or not scored:
        print(f"{player}, you did not score.\n")
        print("The worksheet will not be updated.\n")
        return

    row = coordinates[1] + 2
    col = coordinates[0]
    worksheet_to_update = SHEET.worksheet('board')
    current_value = worksheet_to_update.cell(row, col).value
    new_value = current_value + ", " + player if current_value else player
    worksheet_to_update.update_cell(row, col, new_value)
    print("Worksheet updated successfully.\n")


def did_anybody_win(player, coordinates):
    """
    This function checks if a player has won the game.
    It uses values from the turn() function.
    """
    if not coordinates:
        print("No one won this turn.\n")
        return False

    winning_coordinates = {2: 3, 3: 5, 4: 7, 5: 9, 6: 11, 7: 12,
                           8: 11, 9: 9, 10: 7, 11: 5, 12: 3}

    if coordinates[0] in winning_coordinates.keys():
        if coordinates[1] >= winning_coordinates[coordinates[0]]:
            print(f'Congratulations {player}!! You won the Game!!\n')
            print("If you feel like playing again,\n")
            print("clear all the values from the worksheet before starting.\n")
            print("Meanwhile, be proud of your awesome victory;\n")
            print("it's now on display for everyone to admire!\n")
            return True
    else:
        print("Nobody won during this turn.\n")
        return False



def main():
    """
    This function acts as a control tower
    by calling all the other functions in the right order.
    """
    clear_board()
    presenting_the_game()
    players = naming_the_players()
    target_numbers = [[], []]

    while True:
        target_number, scored = turn(target_numbers[0], players[0])
        target_numbers[0] = target_number
        update_sheet(target_numbers[0], players[0], scored)
        if did_anybody_win(players[0], target_numbers[0]):
            break

        target_number, scored = turn(target_numbers[1], players[1])
        target_numbers[1] = target_number
        update_sheet(target_numbers[1], players[1], scored)
        if did_anybody_win(players[1], target_numbers[1]):
            break


main()