#!/bin/python
from laintracker import Synth, Parser

synth = Synth(speed=0.90)
parser = Parser(name="Better Off Alone", filename="boa.json")

parser.editInstrument(pattern=["01","02","03"], wavetype="square")

for i in range(0,5):
    parser.editOrder(["01","01_2"])
    parser.editOrder(["02","02_2"])
    parser.editOrder(["01","01_3"])
    parser.editOrder(["03","03_2"])

parser.editPattern(pattern="01", note="B4", length=0.08)
parser.editPattern(note="", length=0.24)
parser.editPattern(note="B4", length=0.08)
parser.editPattern(note="")
parser.editPattern(note="G#4")
parser.editPattern(note="", length=0.24)
parser.editPattern(note="B4", length=0.08)
parser.editPattern(note="", length=0.24)
parser.editPattern(note="B4", length=0.08)
parser.editPattern(note="")

for i in range(0,4):
    parser.editPattern(pattern="01_2", note="E3", length=0.16)
    parser.editPattern(note="")

parser.editPattern(pattern="02", note="", length=0.16)
parser.editPattern(note="A#4", length=0.08)
parser.editPattern(note="", length=0.24)
parser.editPattern(note="F#4", length=0.08)
parser.editPattern(note="")
parser.editPattern(note="F#5")
parser.editPattern(note="", length=0.16)
parser.editPattern(note="F#5", length=0.08)
parser.editPattern(note="", length=0.16)
parser.editPattern(note="D#5", length=0.08)
parser.editPattern(note="")

for i in range(0,4):
    parser.editPattern(pattern="02_2", note="D#3", length=0.16)
    parser.editPattern(note="")

for i in range(0,4):
    parser.editPattern(pattern="01_3", note="G#3", length=0.16)
    parser.editPattern(note="")

parser.editPattern(pattern="03", note="", length=0.16)
parser.editPattern(note="A#4", length=0.08)
parser.editPattern(note="", length=0.24)
parser.editPattern(note="F#4", length=0.08)
parser.editPattern(note="")
parser.editPattern(note="E5")
parser.editPattern(note="", length=0.16)
parser.editPattern(note="E5", length=0.08)
parser.editPattern(note="", length=0.16)
parser.editPattern(note="D#5", length=0.08)
parser.editPattern(note="")

for i in range(0,4):
    parser.editPattern(pattern="03_2", note="F#3", length=0.16)
    parser.editPattern(note="")

synth.compile(parser.getData(), verbose=True)
