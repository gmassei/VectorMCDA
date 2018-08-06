#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  fuzzy.py
#  
#  Copyright 2014 gianluca <g_massa@libero.it>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  


class fuzzy:
	def __init__(self):
		return 0
		
		
	def intersection(self,matrix,linguisticMod):
		"""intersect with AND/min operator all the alternatives \
		 and get the ranking values for each alternative"""
		weigtedMatrix=[[r**w for r,w in zip(row,linguisticMod)] for row in matrix]
		rank=[min(row) for row in weigtedMatrix]
		return rank
		
	def union(self,matrix,linguisticMod):
		"""intersect with AND/min operator all the alternatives \
		 and get the ranking values for each alternative"""
		weigtedMatrix=[[r**w for r,w in zip(row,linguisticMod)] for row in matrix]
		rank=[min(row) for row in weigtedMatrix]
		return rank
		


def main():
	print("fuzzy mcda model")
	return 0

if __name__ == '__main__':
	main()
