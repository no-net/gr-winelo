""" This module includes hw models and routines for rate adjustments. """
# No HW influence (no rate adjustments possible)
from none_cc import none_cc
# Mixing-only HW influence (incl. rate adjustments)
from mixing_only_cc import mixing_only_cc
# Basic generic HW influences
from basic_cc import basic_cc
# Generic (HW-)impairments
import generic_impairments
