#! /usr/bin/env python
# CCScriptWriter
# Extracts the dialogue from Mother 2 and outputs it into a CCScript file.

import argparse
import array
import math
import os
import re
import sys
import time

import yaml
from functools import reduce

 
#############
# CONSTANTS #
#############

# Based on Coop's M2 ccc fork
CHARACTER_MAP = {
    0x20: ' ',
    0x25: 'ー',
    0x28: '!',
    0x29: '?',
    0x2A: 'α',
    0x2B: 'β',
    0x2C: 'γ',
    0x2D: 'Σ',
    0x2E: 'Ω',
    0x2F: '/',
    0x30: '0',
    0x31: '1',
    0x32: '2',
    0x33: '3',
    0x34: '4',
    0x35: '5',
    0x36: '6',
    0x37: '7',
    0x38: '8',
    0x39: '9',
    0x3A: '(',
    0x3B: ')',
    0x3C: '「',
    0x3D: '」',
    0x3E: '♪',
    0x3F: '○',
    0x40: '•',
    0x41: 'A',
    0x42: 'B',
    0x43: 'C',
    0x44: 'D',
    0x45: 'E',
    0x46: 'F',
    0x47: 'G',
    0x48: 'H',
    0x49: 'I',
    0x4A: 'J',
    0x4B: 'K',
    0x4C: 'L',
    0x4D: 'M',
    0x4E: 'N',
    0x4F: 'O',
    0x50: 'P',
    0x51: 'Q',
    0x52: 'R',
    0x53: 'S',
    0x54: 'T',
    0x55: 'U',
    0x56: 'V',
    0x57: 'W',
    0x58: 'X',
    0x59: 'Y',
    0x5A: 'Z',
    0x5B: ':',
    0x5C: '・',
    0x5D: '…',
    0x5E: '[5E]',
    0x5F: '.',
    0x60: 'あ',
    0x61: 'ぁ',
    0x62: 'か',
    0x63: 'が',
    0x64: 'さ',
    0x65: 'ざ',
    0x66: 'た',
    0x67: 'だ',
    0x68: 'な',
    0x69: 'は',
    0x6A: 'ば',
    0x6B: 'ぱ',
    0x6C: 'ま',
    0x6D: 'や',
    0x6E: 'ゃ',
    0x6F: 'ら',
    0x70: 'い',
    0x71: 'ぃ',
    0x72: 'き',
    0x73: 'ぎ',
    0x74: 'し',
    0x75: 'じ',
    0x76: 'ち',
    0x77: 'ぢ',
    0x78: 'に',
    0x79: 'ひ',
    0x7A: 'び',
    0x7B: 'ぴ',
    0x7C: 'み',
    0x7D: 'わ',
    0x7E: 'っ',
    0x7F: 'り',
    0x80: 'う',
    0x81: 'ぅ',
    0x82: 'く',
    0x83: 'ぐ',
    0x84: 'す',
    0x85: 'ず',
    0x86: 'つ',
    0x87: 'づ',
    0x88: 'ぬ',
    0x89: 'ふ',
    0x8A: 'ぶ',
    0x8B: 'ぷ',
    0x8C: 'む',
    0x8D: 'ゆ',
    0x8E: 'ゅ',
    0x8F: 'る',
    0x90: 'え',
    0x91: 'ぇ',
    0x92: 'け',
    0x93: 'げ',
    0x94: 'せ',
    0x95: 'ぜ',
    0x96: 'て',
    0x97: 'で',
    0x98: 'ね',
    0x99: 'へ',
    0x9A: 'べ',
    0x9B: 'ぺ',
    0x9C: 'め',
    0x9D: 'ん',
    0x9E: 'を',
    0x9F: 'れ',
    0xA0: 'お',
    0xA1: 'ぉ',
    0xA2: 'こ',
    0xA3: 'ご',
    0xA4: 'そ',
    0xA5: 'ぞ',
    0xA6: 'と',
    0xA7: 'ど',
    0xA8: 'の',
    0xA9: 'ほ',
    0xAA: 'ぼ',
    0xAB: 'ぽ',
    0xAC: 'も',
    0xAD: 'よ',
    0xAE: 'ょ',
    0xAF: 'ろ',
    0xB0: 'ア',
    0xB1: 'ァ',
    0xB2: 'カ',
    0xB3: 'ガ',
    0xB4: 'サ',
    0xB5: 'ザ',
    0xB6: 'タ',
    0xB7: 'ダ',
    0xB8: 'ナ',
    0xB9: 'ハ',
    0xBA: 'バ',
    0xBB: 'パ',
    0xBC: 'マ',
    0xBD: 'ヤ',
    0xBE: 'ャ',
    0xBF: 'ラ',
    0xC0: 'イ',
    0xC1: 'ィ',
    0xC2: 'キ',
    0xC3: 'ギ',
    0xC4: 'シ',
    0xC5: 'ジ',
    0xC6: 'チ',
    0xC7: 'ヂ',
    0xC8: 'ニ',
    0xC9: 'ヒ',
    0xCA: 'ビ',
    0xCB: 'ピ',
    0xCC: 'ミ',
    0xCD: 'ワ',
    0xCE: 'ッ',
    0xCF: 'リ',
    0xD0: 'ウ',
    0xD1: 'ゥ',
    0xD2: 'ク',
    0xD3: 'グ',
    0xD4: 'ス',
    0xD5: 'ズ',
    0xD6: 'ツ',
    0xD7: 'ヅ',
    0xD8: 'ヌ',
    0xD9: 'フ',
    0xDA: 'ブ',
    0xDB: 'プ',
    0xDC: 'ム',
    0xDD: 'ユ',
    0xDE: 'ュ',
    0xDF: 'ル',
    0xE0: 'エ',
    0xE1: 'ェ',
    0xE2: 'ケ',
    0xE3: 'ゲ',
    0xE4: 'セ',
    0xE5: 'ゼ',
    0xE6: 'テ',
    0xE7: 'デ',
    0xE8: 'ネ',
    0xE9: 'ヘ',
    0xEA: 'ベ',
    0xEB: 'ペ',
    0xEC: 'メ',
    0xED: 'ン',
    0xEE: '[EE]',
    0xEF: 'レ',
    0xF0: 'オ',
    0xF1: 'ォ',
    0xF2: 'コ',
    0xF3: 'ゴ',
    0xF4: 'ソ',
    0xF5: 'ゾ',
    0xF6: 'ト',
    0xF7: 'ド',
    0xF8: 'ノ',
    0xF9: 'ホ',
    0xFA: 'ボ',
    0xFB: 'ポ',
    0xFC: 'モ',
    0xFD: 'ヨ',
    0xFE: 'ョ',
    0xFF: 'ロ',
}

D = [0x45, 0x41, 0x52, 0x54, 0x48, 0x20, 0x42, 0x4f, 0x55, 0x4E, 0x44]

# TODO - Add remaining pointers (flyover text, etc) here
#      - I also commented out the stuff that processes SPECIAL_POINTERS and ASM_POINTERS.
#      - Handle flyover text format a lot nicer (may need compiler changes idk)
TEXT_DATA = [
    [0x050000, 0x057FA7],
    [0x058000, 0x05FE4D],
    [0x060000, 0x067C03],
    [0x068000, 0x06FB86],
    [0x070000, 0x077FE1],
    [0x078000, 0x07FC11],
    [0x080000, 0x087E85],
    [0x088000, 0x08FEDE],
    [0x090000, 0x097F65],
    [0x098000, 0x09E2A1],
]
#COMPRESSED_TEXT_PTRS = 0x8cded <- M2 doesn't seem to have this.

CONTROL_CODES = {0x00: 0, 0x01: 0, 0x02: 0, 0x03: 0, 0x04: 2, 0x05: 2, 0x06: 6,
                 0x07: 2, 0x08: 4, 0x09: None, 0x0a: 4, 0x0b: 1, 0x0c: 1,
                 0x0d: 1, 0x0e: 1, 0x0f: 0, 0x10: 1, 0x11: 0, 0x12: 0, 0x13: 0,
                 0x14: 0, 0x15: 1, 0x16: 1, 0x17: 1, 0x18: None, 0x19: None,
                 0x1a: None, 0x1b: None, 0x1c: None, 0x1d: None, 0x1e: None,
                 0x1f: None, 0x20: 0, 0x21: 0, 0x22: 0, 0x23: 0, 0x24: 0,
                 0x25: 0, 0x26: 0, 0x27: 0, 0x28: 0, 0x29: 0, 0x2a: 0, 0x2b: 0,
                 0x2c: 0, 0x2d: 0, 0x2e: 0, 0x2f: 0, 0x30: 0}

PATTERNS = [r"\[(06 \w\w \w\w )(\w\w \w\w \w\w \w\w)]",
            r"\[(08 )(\w\w \w\w \w\w \w\w)]",
            r"\[(09 \w\w)(( \w\w \w\w \w\w \w\w)+)\]",
            r"\[(0A )(\w\w \w\w \w\w \w\w)\]",
            r"\[(1A 0[0|1])(( \w\w \w\w \w\w \w\w)+)( \w\w)\]",
            r"\[(1B 0[2|3] )(\w\w \w\w \w\w \w\w)\]",
            r"\[(1F 63 )(\w\w \w\w \w\w \w\w)\]",
            r"\[(1F C0 \w\w)(( \w\w \w\w \w\w \w\w)+)\]"]
REPLACE = [["[13][02]\"", "\" end"], ["[03][00]", "\" next\n\""],
           ["[00]", "\" linebreak\n\""], ["[01]", "\" newline\n\""],
           ["[02]\"", "\" eob"], ["[0F]", "{inc}"], ["[0D 00]", "{rtoarg}"],
           ["[0D 01]", "{ctoarg}"], ["[12]", "{clearline}"], ["[13]", "{wait}"],
           ["[14]", "{prompt}"], ["[18 00]", "{window_closetop}"],
           ["[18 04]", "{window_closeall}"], ["[18 06]", "{window_clear}"],
           ["[18 0A]", "{open_wallet}"], ["[1B 00]", "{store_registers}"],
           ["[1B 01]", "{load_registers}"], ["[1B 04]", "{swap}"],
           ["[1C 04]", "{open_hp}"], ["[1C 0D]", "{user}"],
           ["[1C 0E]", "{target}"], ["[1C 0F]", "{delta}"],
           ["[1C 08 01]  ", "{smash}"], ["[1C 08 02]  ", "{youwon}"],
           ["[1F 01 02]", "{music_stop}"], ["[1F 03]", "{music_resume}"],
           ["[1F 05]", "{music_switching_off}"],
           ["[1F 06]", "{music_switching_on}"], ["[1F B0]", "{save}"],
           ["[1F 30]", "{font_normal}"], ["[1F 31]", "{font_saturn}"],
           [" \"\"", ""], [" \"\" ", " "], [" \"\"", ""], ["\"\" ", ""]]
RE_REPLACE = [r"\[(0[4|5|7])( \w\w \w\w)\]",
              r"\[(10|18 01|18 03|0E|0B|0C])( \w\w)\]",
              r"\[(1F 02|1F 00 00|1F 07])( \w\w)\]"]

COILSNAKE_FILES = ["attract_mode_txt.yml", "battle_action_table.yml",
                   "enemy_configuration_table.yml", "map_doors.yml",
                   "item_configuration_table.yml", "npc_config_table.yml",
                   "psi_ability_table.yml", "telephone_contacts_table.yml",
                   "timed_delivery_table.yml"]

COILSNAKE_POINTERS = ["Text Address", "Death Text Pointer",
                      "Encounter Text Pointer", "Help Text Pointer",
                      "Text Pointer 1", "Text Pointer 2", "Text Pointer",
                      "Delivery Failure Text Pointer",
                      "Delivery Success Text Pointer", "Pointer"]

SPECIAL_POINTERS = [0x4737C, 0x47380, 0x47384, 0x47388, 0x4738C, 0x47390, 
                    0x47394, 0x47398, 0xCF728] #0x49ea4, 0x49ea8, 0x49eac, 0x49eb0, 0x49eb4, 0x49eb8, 0x49ebc, 0x49ec0, 0xcffd5

ASM_POINTERS = [0x47291, 0x4729D, 0x4C28E] #0x49dbd, 0x49dc9, 0x4f252

HEADER = """/*
 * EarthBound Text Dump
 * Time: {}
 * Generated using CCScriptWriter.
 */

""".format(time.strftime("%H:%M:%S - %d/%m/%Y"))


#####################
# UTILITY FUNCTIONS #
#####################

# Find the closest and lowest key.
def FindClosest(dictionary, searchKey):

    lower = 0
    for key in sorted(dictionary):
        if searchKey - key >= 0:
            lower = key
        else:
            higher = key
    return lower, higher

# Format a hex number to a control code format.
def FormatHex(intNum):

    hexNum = hex(intNum).lstrip("0x").upper()
    if not hexNum:
        hexNum = "00"
    elif len(hexNum) == 1:
        hexNum = "0{}".format(hexNum)
    return hexNum

# Converts an SNES address to a hexadecimal address.
def FromSNES(snesNum):

    if snesNum.count("0") == 8:
        return 0
    return int("".join(reversed(snesNum.strip().split())), 16)

# Converts a hexadecimal address to an SNES address.
def ToSNES(hexNum):

    if hexNum == 0:
        return "00 00 00 00"
    h = hex(hexNum).lstrip("0x").upper()
    return " ".join(reversed(re.findall("\w\w", "{0:0>8}".format(h))))


##################
# CCScriptWriter #
##################


class CCScriptWriter:

    def __init__(self, romFile, outputDirectory, raw=False):

        # Declare our variables.
        self.asmPointers = {}
        self.data = array.array("B")
        self.dialogue = {}
        self.dataFiles = {}
        self.outputDirectory = outputDirectory
        self.pointers = []
        self.raw = raw
        self.specialPointers = {}

        # Get the data from the ROM file.
        self.data.fromfile(romFile, int(os.path.getsize(romFile.name)))

        # Check for a headered HiROM.
        try:
            if ~self.data[0x101dc] & 0xff == self.data[0x101de] \
              and ~self.data[0x101dd] & 0xff == self.data[0x101df] \
              and self.data[0xffc0+0x200:0xffc0 + 0x200 + len(D)].tolist() == D:
                self.data = self.data[0x200:]
            romFile.close()
        except IndexError:
            pass

        # Check for a headered LoROM.
        try:
            if ~self.data[0x81dc] & 0xff == self.data[0x81de] \
              and ~self.data[0x81dd] & 0xff == self.data[0x81df] \
              and self.data[0xffc0+0x200:0xffc0 + 0x200 + len(D)].tolist() == D:
                self.data = self.data[0x200:]
        except IndexError:
            pass

        if self.data is None:
            print("Invalid EarthBound ROM. Aborting.")
            sys.exit(1)

    # Loads the dialogue from the text banks in the ROM.
    def loadDialogue(self, loadCoilSnake=False):

        # Start looping over every block in the dialogue.
        print("Loading dialogue...")
        for section in TEXT_DATA:
            i = section[0]
            dataType = 0
            if section[0] == 0x211602 or section[0] == 0x211B1C \
              or section[0] == 0x212085:
                dataType = 1
            elif section[0] == 0x213596:
                dataType = 2
            while i < section[1]:
                block = i + 0xc00000
                self.dialogue[block], i = self.getText(i, None, dataType)

        # Optionally load the CoilSnake pointers.
        if loadCoilSnake:
            o = os.path.join(self.outputDirectory, os.path.pardir)
            project = os.path.join(o, "Project.snake")
            try:
                with open(project) as f: pass
            except IOError:
                print("Failed to open \"{}\". Invalid CoilSnake project. "
                      "Aborting.".format(project))
                sys.exit(1)
            for fileName in COILSNAKE_FILES:
                csFile = open(os.path.join(o, fileName), "r")
                yamlData = yaml.load(csFile, Loader=yaml.CSafeLoader)
                csFile.close()
                if fileName != "map_doors.yml":
                    for e, v in yamlData.items():
                        for p in COILSNAKE_POINTERS:
                            if p in v:
                                try:
                                    pointer = int(v[p][1:], 16)
                                    if pointer > 0xc00000 \
                                       and pointer not in self.dialogue:
                                        self.pointers.append(pointer)
                                except ValueError:
                                    self.pointers.append(int(v[p][12:], 16))
                else:
                    p = "Text Pointer"
                    for e, v in yamlData.items():
                        for s, d in v.items():
                            if not d: continue
                            for k in d:
                                if p in k:
                                    try:
                                        pointer = int(k[p][1:], 16)
                                        if pointer > 0xc00000 \
                                           and pointer not in self.dialogue:
                                            self.pointers.append(pointer)
                                    except ValueError:
                                        self.pointers.append(int(k[p][12:], 16))

        # Find the special pointed-to locations.
        for p in SPECIAL_POINTERS:
            address = ""
            i = p
            while i < p + 4:
                address += " {}".format(FormatHex(self.data[i]))
                i += 1
            self.pointers.append(FromSNES(address))

        # Add new blocks as needed by the pointers.
        print("Checking pointers...")
        pointers = [_f for _f in sorted(set(self.pointers)) if _f]
        self.pointers = []
        for address in self.dialogue:
            if address in pointers:
                pointers.remove(address)
        for pointer in pointers:
            try:
                lower, higher = FindClosest(self.dialogue, pointer)
            except UnboundLocalError:
                continue
            block, i = self.getText(lower - 0xc00000, pointer - 0xc00000)
            self.dialogue[lower] = ["{}[0A {}]".format(block[0],
                                                       ToSNES(pointer)),
                                    block[1]]
            self.dialogue[pointer], i = self.getText(pointer - 0xc00000)

        # Assign each group to its output file.
        for k, block in enumerate(sorted(self.dialogue)):
            self.dataFiles[block] = "data_{0:0>2}".format(k // 100)

        # # Add special pointer locations.
        # for p in SPECIAL_POINTERS:
        #     address = ""
        #     i = p
        #     while i < p + 4:
        #         address += " {}".format(FormatHex(self.data[i]))
        #         i += 1
        #     address = FromSNES(address)
        #     m = self.dataFiles[address]
        #     h = hex(address)
        #     self.specialPointers[p] = "[{{e({}.l_{})}}]".format(m, h)
        # for a in ASM_POINTERS:
        #     if self.data[a + 3] == 0x85:
        #         address = FromSNES("{} {} {} {}".format(
        #                            FormatHex(self.data[a + 1]),
        #                            FormatHex(self.data[a + 2]),
        #                            FormatHex(self.data[a + 6]),
        #                            FormatHex(self.data[a + 7])))
        #         t = 0
        #     elif self.data[a + 3] == 0x8d:
        #         address = FromSNES("{} {} {} {}".format(
        #                            FormatHex(self.data[a + 1]),
        #                            FormatHex(self.data[a + 2]),
        #                            FormatHex(self.data[a + 7]),
        #                            FormatHex(self.data[a + 8])))
        #         t = 1
        #     m = self.dataFiles[address]
        #     h = hex(address)
        #     self.asmPointers[a] = ["{}.l_{}".format(m, h), t]

    # Performs various replacements on the dialogue blocks.
    def processDialogue(self):

        print("Processing dialogue...")
        f = self.replaceWithLabel
        for block in self.dialogue:
            b = self.dialogue[block][0]
            b = "\"{}\"".format(b)

            # Replace compressed text.
            # if not self.raw:
                # b = re.sub(r"\[(15|16|17) (\w\w)\]", #self.replaceCompressedText,
                        #    b)

            # Replace all pointers with their label form.
            for p in PATTERNS:
                try:
                    b = re.sub(p, f, b)
                except (IndexError, KeyError):
                    continue

            # Replace control codes and more with CCScript syntax.
            if not self.raw:
                for r in REPLACE:
                    b = b.replace(r[0], r[1])
                for r in RE_REPLACE:
                    b = re.sub(r, self.replaceWithCCScript, b)

            self.dialogue[block][0] = b

    # Outputs the processed dialogue to the specified output directory.
    def outputDialogue(self, outputCoilSnake=False):

        # Initialize the output directory.
        print("Writing data...")
        if not os.path.exists(self.outputDirectory):
            os.makedirs(self.outputDirectory)
        o = self.outputDirectory

        # Prepare the main file containing ROM addresses.
        mainFile = open(os.path.join(o, "main.ccs"), "w")
        m = mainFile.write
        m(HEADER)
        m("// DO NOT EDIT THIS FILE.\n")
        m("\ncommand e(label) \"{long label}\"")
        m("\ncommand _lasmptr(loc,target) {\n    ROMTBL[loc, 1, 1] = short [0] "
          "target\n    ROMTBL[loc, 7, 1] = short [1] target\n}")

        # Output each data_xx.ccs file.
        numFiles = math.ceil(len(self.dialogue) / 100)
        i = 0
        while i <= numFiles:
            f = "data_{0:0>2}.".format(i)
            fileName = "{}ccs".format(f)
            dataFile = open(os.path.join(o, fileName), "w")
            d = dataFile.write
            d(HEADER)
            d("command e(label) \"{long label}\"\n")
            d("\n// Text Data\n")
            dialogue = sorted(self.dialogue)[i * 100:i * 100 + 100]
            m("\n\n// Memory Overwriting: {}".format(fileName))
            for block in dialogue:
                d("l_{}:\n".format(hex(block)))
                lines = self.dialogue[block][0].split("\n")
                for line in lines:
                    l = line.replace(f, "")
                    d("    {}\n".format(l))
                d("\n")
                if self.dialogue[block][1] >= 5:
                    m("\nROM[{}] = goto({}l_{})".format(hex(block), f,
                                                        hex(block)))
            dataFile.close()
            i += 1

        # Take care of the special pointers (both SNES and ASM type).
        m("\n\n// Special Pointers")
        for k, p in self.specialPointers.items():
            m("\nROM[{}] = \"{}\"".format(hex(k + 0xc00000), p))
        for k, p in self.asmPointers.items():
            if p[1] == 0:
                m("\n_asmptr({}, {})".format(hex(k + 0xc00000), p[0]))
            elif p[1] == 1:
                m("\n_lasmptr({}, {})".format(hex(k + 0xc00000), p[0]))
        mainFile.close()

        # Optionally output to the CoilSnake project.
        if outputCoilSnake:
            self.outputToCoilSnakeProject()

    # Modifies the contents of a CoilSnake project to point to the new values.
    def outputToCoilSnakeProject(self):

        print("Modifying CoilSnake project...")
        o = os.path.join(self.outputDirectory, os.path.pardir)
        for fileName in COILSNAKE_FILES:
            csFile = open(os.path.join(o, fileName), "r")
            yamlData = yaml.load(csFile, Loader=yaml.CSafeLoader)
            if fileName != "map_doors.yml":
                for e, v in yamlData.items():
                    pointers = {}
                    for p in COILSNAKE_POINTERS:
                        if p in v:
                            try:
                                pointers[p] = int(v[p][1:], 16)
                                if pointers[p] < 0xc00000:
                                    del pointers[p]
                            except ValueError:
                                pointers[p] = int(v[p][12:], 16)
                    if not pointers:
                        continue
                    for k, v in pointers.items():
                        f = self.dataFiles[v]
                        yamlData[e][k] = "{}.l_{}".format(f, hex(v))
            else:
                p = "Text Pointer"
                for e, v in yamlData.items():
                    for s, d in v.items():
                        if not d: continue
                        for n, k in enumerate(d):
                            pointers = {}
                            if p in k:
                                try:
                                    pointers[p] = int(k[p][1:], 16)
                                    if pointers[p] < 0xc00000:
                                        del pointers[p]
                                except ValueError:
                                    pointers[p] = int(k[p][12:], 16)
                            if not pointers:
                                continue
                            for a, b in pointers.items():
                                f = self.dataFiles[b]
                                yamlData[e][s][n][a] = "{}.l_{}".format(f,
                                                                        hex(b))
            csFile = open(os.path.join(o, fileName), "w")
            output = yaml.dump(yamlData, default_flow_style=False,
                      Dumper=yaml.CSafeDumper)
            output = re.sub("Event Flag: (\d+)",
                   lambda i: "Event Flag: " + hex(int(i.group(0)[12:])), output)
            csFile.write(output)
            csFile.close()

    # Gets the text at a specified location in memory; if stop is specified, it
    # will forcibly stop looking once it is reached. The third parameter
    # specifies whether the data block is a normal block, a coffee scene type
    # block or a staff list block.
    def getText(self, i, stop=None, dataType=False):

        block = ""
        start = i
        text = False
        normal_block_expect_02 = False

        while True:
            if stop and stop == i:
                break
            c = self.data[i]
            i += 1
            # Is it a normal block?
            if dataType == 0:
                # Check if it's a control code.
                if c <= 0x30:
                    code = CONTROL_CODES[c]
                    if isinstance(code, int):
                        length = code
                    else:
                        length = self.getLength(i)
                    block += "[{}".format(FormatHex(c))

                    # Mark if we expect an [02] before the end of the block
                    if c == 0x19:
                        normal_block_expect_02 = True

                    # Get the rest of the control code.
                    codeEnd = i + length
                    while i < codeEnd:
                        block += " {}".format(FormatHex(self.data[i]))
                        i += 1
                    block += "]"

                    # Stop if this is a block-ending character.
                    if c == 0x02 and normal_block_expect_02:
                        # But don't stop if we expect an [02] that doesn't end the block
                        normal_block_expect_02 = False
                    elif c == 0x02 or c == 0x0A:
                        break
                # Check if it's a special character.
                # elif c == 0x52 or c == 0x8b or c == 0x8c or c == 0x8d:
                #     block += "[{}]".format(FormatHex(c))
                    
                # Looks like it's a normal character.
                else:
                    try:
                        block += CHARACTER_MAP[c]
                    except KeyError as e:
                        raise RuntimeError("Unknown character in script: {}".format(hex(c))) from e
            elif dataType == 1:
                # End of text block.
                # (I assume...)
                if c == 0x00:
                    block += "[ 00 ]"
                    break
                
                # Text character (flyover encoding)
                elif c == 0x80:
                    block += " {{short 0x80{}}} ".format(FormatHex(self.data[i]))
                    i += 1
                
                # Everything else is control codes I guess
                else:
                    block += "[ {} ]".format(FormatHex(c))
                
                # # Move the text over a distance noted by XX.
                # elif c == 0x01:
                #     block += "[ 01 {} ]".format(FormatHex(self.data[i]))
                #     i += 1
                # # Move the text down a distance noted by XX.
                # elif c == 0x02:
                #     block += "[ 02 {} ]".format(FormatHex(self.data[i]))
                #     i += 1
                # # Print the name of character XX (01 = Ness, XX[1,4]).
                # elif c == 0x08:
                #     block += "[ 08 {} ]".format(FormatHex(self.data[i]))
                #     i += 1
                # # Drop down one line.
                # elif c == 0x09:
                #     block += "[ 09 ]"
                # # Looks like it's a normal character.
                # else:
                #     block += chr(c - 0x30)
            elif dataType == 2:
                if c in (0x00, 0x01, 0x02, 0x04, 0xff):
                    if not text:
                        block += "[ {} ]".format(FormatHex(c))
                    else:
                        block += " ][ {} ]".format(FormatHex(c))
                        text = False
                elif c == 0x03:
                    if not text:
                        block += "[ 03 {} ]".format(FormatHex(self.data[i]))
                    else:
                        block += " ][ 03 {} ]".format(FormatHex(self.data[i]))
                        text = False
                    i += 1
                else:
                    if not text:
                        block += "["
                        text = True
                    block += " {}".format(FormatHex(c))
                if c == 0x00:
                    block += "\"\n\""
                if c == 0xff:
                    break

        # Check if it's referencing a location in memory.
        for pattern in PATTERNS:
            matches = re.findall(pattern, block)
            for match in matches:
                pointer = match[1].strip()
                if len(match) < 3:
                    self.pointers.append(FromSNES(pointer))
                else:
                    p = pointer.split()
                    idx = 0
                    while idx < len(p):
                        a = FromSNES(" ".join(map(str, p[idx:idx + 4])))
                        self.pointers.append(a)
                        idx += 4

        return [block, i - start], i

    # Gets the length of a control code with variable length.
    def getLength(self, i):

        c = self.data[i - 1]
        if c == 0x09:
            return 1 + self.data[i] * 4
        elif c == 0x1B:
            if self.data[i] == 0x02 or self.data[i] == 0x03:
                return 5
            else:
                return 1
        elif c == 0x1E:
            if self.data[i] == 0x09:
                return 5
            else:
                return 3
        elif c == 0x1F:
            combos = {0x00: 3, 0x01: 2, 0x02: 2, 0x03: 1, 0x04: 2, 0x05: 1,
                      0x06: 1, 0x07: 2, 0x11: 2, 0x12: 2, 0x13: 3, 0x14: 2,
                      0x15: 6, 0x16: 4, 0x17: 6, 0x18: 8, 0x19: 8, 0x1A: 4,
                      0x1B: 3, 0x1C: 3, 0x1D: 2, 0x1E: 4, 0x1F: 4, 0x20: 3,
                      0x21: 2, 0x23: 3, 0x30: 1, 0x31: 1, 0x41: 2, 0x50: 1,
                      0x51: 1, 0x52: 2, 0x60: 2, 0x61: 1, 0x62: 2, 0x63: 5,
                      0x64: 1, 0x65: 1, 0x66: 7, 0x67: 2, 0x68: 1, 0x69: 1,
                      0x71: 3, 0x81: 3, 0x83: 3, 0x90: 1, 0xA0: 1, 0xA1: 1,
                      0xA2: 1, 0xB0: 1, 0xC0: None, 0xD0: 2, 0xD1: 1, 0xD2: 2,
                      0xD3: 2, 0xE1: 4, 0xE4: 4, 0xE5: 2, 0xE6: 3, 0xE7: 3,
                      0xE8: 2, 0xE9: 3, 0xEA: 3, 0xEB: 3, 0xEC: 3, 0xED: 1,
                      0xEE: 3, 0xEF: 3, 0xF0: 1, 0xF1: 5, 0xF2: 5, 0xF3: 4,
                      0xF4: 3}
            if self.data[i] != 0xC0:
                return combos[self.data[i]]
            else:
                numPointers = self.data[i + 1]
                return 2 + numPointers * 4
        elif c == 0x18:
            combos = {0x00: 1, 0x01: 2, 0x02: 1, 0x03: 2, 0x04: 1, 0x05: 3,
                      0x06: 1, 0x07: 6, 0x08: 2, 0x09: 2, 0x0A: 1, 0x0D: 3}
        elif c == 0x19:
            combos = {0x02: 1, 0x04: 1, 0x05: 4, 0x10: 2, 0x11: 2, 0x14: 1,
                      0x16: 3, 0x18: 2, 0x19: 3, 0x1A: 2, 0x1B: 2, 0x1C: 3,
                      0x1D: 3, 0x1E: 1, 0x1F: 1, 0x20: 1, 0x21: 2, 0x22: 5,
                      0x23: 6, 0x24: 6, 0x25: 2, 0x26: 2, 0x27: 2, 0x28: 2}
        elif c == 0x1A:
            combos = {0x00: 18, 0x01: 18, 0x04: 1, 0x05: 3, 0x06: 2, 0x07: 1,
                      0x08: 1, 0x09: 1, 0x0a: 1, 0x0B: 1}
        elif c == 0x1C:
            combos = {0x00: 2, 0x01: 2, 0x02: 2, 0x03: 2, 0x04: 1, 0x05: 2,
                      0x06: 2, 0x07: 2, 0x08: 2, 0x09: 1, 0x0A: 5, 0x0B: 5,
                      0x0C: 2, 0x0D: 1, 0x0E: 1, 0x0F: 1, 0x11: 2, 0x12: 2,
                      0x13: 3, 0x14: 2, 0x15: 2}
        elif c == 0x1D:
            combos = {0x00: 3, 0x01: 3, 0x02: 2, 0x03: 2, 0x04: 3, 0x05: 3,
                      0x06: 5, 0x07: 5, 0x08: 3, 0x09: 3, 0x0A: 2, 0x0B: 2,
                      0x0C: 3, 0x0D: 4, 0x0E: 3, 0x0F: 3, 0x10: 3, 0x11: 3,
                      0x12: 3, 0x13: 3, 0x14: 5, 0x15: 3, 0x17: 5, 0x18: 2,
                      0x19: 2, 0x20: 1, 0x21: 2, 0x22: 1, 0x23: 2, 0x24: 2}
        try:
            return combos[self.data[i]]
        except:
            return 0

    # # Replaces the compressed text control codes with their values.
    # def replaceCompressedText(self, matchObj):

    #     bank = int(matchObj.groups()[0], 16) - 0x15
    #     idx = int(matchObj.groups()[1], 16)
    #     p = COMPRESSED_TEXT_PTRS + (bank * 0x100 + idx) * 4
    #     pointer = self.data[p:p + 4]
    #     pointer.reverse()
    #     pointer = int(reduce(lambda x, y: (x << 8) | y, pointer)) - 0xc00000
    #     returnString = ""
    #     while self.data[pointer] != 0:
    #         returnString += chr(self.data[pointer] - 0x30)
    #         pointer += 1
    #     return returnString

    # Replaces the control code's pointer(s) with labels instead.
    def replaceWithLabel(self, matchObj):

        prefix = matchObj.groups()[0]
        if len(matchObj.groups()) < 3:
            pointer = matchObj.groups()[1]
            address = FromSNES(pointer)
            if not address:
                return "[{}00 00 00 00]".format(prefix)
            m = self.dataFiles[address]
            h = hex(address)
            if prefix == "0A " and not self.raw:
                return "\" goto({}.l_{}) \"".format(m, h)
            elif prefix == "08 " and not self.raw:
                return "\" call({}.l_{}) \"".format(m, h)
            else:
                return "[{}{{e({}.l_{})}}]".format(prefix, m, h)
        else:
            pointers = matchObj.groups()[1].split()
            returnString = "[{}".format(prefix)
            i = 0
            while i < len(pointers):
                address = FromSNES(" ".join(map(str, pointers[i:i + 4])))
                if address <= 0:
                    returnString += " 00 00 00 00"
                else:
                    returnString += " {{e({}.l_{})}}".format(
                                                      self.dataFiles[address],
                                                      hex(address))
                i += 4
            if len(matchObj.groups()) == 4:
                returnString += matchObj.groups()[3]
            returnString += "]"
            return returnString

    # Replace with CCScript syntax.
    def replaceWithCCScript(self, matchObj):

        t = matchObj.groups()[0]
        a = FromSNES(matchObj.groups()[1])
        if t == "04":
            return "{{set(flag {})}}".format(a)
        elif t == "05":
            return "{{unset(flag {})}}".format(a)
        elif t == "07":
            return "{{isset(flag {})}}".format(a)
        elif t == "10":
            return "{{pause({})}}".format(a)
        elif t == "18 01":
            return "{{window_open({})}}".format(a)
        elif t == "18 03":
            return "{{window_switch({})}}".format(a)
        elif t == "0E":
            return "{{counter({})}}".format(a)
        elif t == "0B":
            return "{{result_is({})}}".format(a)
        elif t == "0C":
            return "{{result_not({})}}".format(a)
        elif t == "1F 02":
            return "{{sound({})}}".format(a)
        elif t == "1F 00 00":
            return "{{music({})}}".format(a)
        elif t == "1F 07":
            return "{{music_effect({})}}".format(a)


########
# MAIN #
########

def main():
    try:
        print("CCScriptWriter v1.1")
        start = time.time()

        # Get the input and output files from the terminal.
        parser = argparse.ArgumentParser(description="Extracts the dialogue "
                                         "from EarthBound and outputs it into a"
                                         " CCScript file.")
        parser.add_argument("rom", metavar="INPUT",
                            type=argparse.FileType("rb"),
                            help="the source ROM file")
        parser.add_argument("output", metavar="OUTPUT", type=str,
                            help="the folder to output to (if --coilsnake is "
                            "specified, this must be the location of the "
                            "CoilSnake project; the dialogue will be placed in "
                            "OUTPUT/ccscript/)")
        parser.add_argument("-c", "--coilsnake", help="indicates that "
                            "CCScriptWriter should also modify a CoilSnake "
                            "project", action="store_true")
        parser.add_argument("-r", "--raw", help="specifies that the control "
                            "codes should be outputted raw, without CCScript "
                            "replacements", action="store_true")
        args = parser.parse_args()

        # Run the program.
        if args.coilsnake:
            output = os.path.join(args.output, "ccscript")
        else:
            output = args.output
        main = CCScriptWriter(args.rom, output, args.raw)
        main.loadDialogue(args.coilsnake)
        main.processDialogue()
        main.outputDialogue(args.coilsnake)
        print("Complete. Time: {:.2f}s".format(float(time.time() - start)))
    except KeyboardInterrupt:
        print("\rProgram execution aborted.")

if __name__ == "__main__":
    main()
