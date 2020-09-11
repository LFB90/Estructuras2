ALL: BUILD


CHECK:
	pylint branch.py
	pyflakes branch.py

BUILD:
	#gunzip -c branch-trace-gcc.trace.gz|branch -s<#>-bp<#>-gh<#>-ph<#>
	
	#Final
	#gunzip -c branch-trace-gcc.trace.gz|python3 branch.py -s 4
	#gunzip -c branch-trace-gcc.trace.gz|python3 branch.py -s 5 -bp 1 -ph 3
	#gunzip -c branch-trace-gcc.trace.gz|python3 branch.py -s 5 -bp 2 -gh 4
	gunzip -c branch-trace-gcc.trace.gz|python3 branch.py -s 5 -bp 3 -gh 5 -ph 3
	
	#Test
	#gunzip -c branch-trace-gcc.trace.gz|python3 branch.py -s 5 -countsPC "20"
	#gunzip -c branch-trace-gcc.trace.gz|python3 branch.py -s 5 -countsPC "20" -bp 1 -ph 3
	#gunzip -c branch-trace-gcc.trace.gz|python3 branch.py -s 5 -countsPC "20" -bp 2 -gh 4
	#gunzip -c branch-trace-gcc.trace.gz|python3 branch.py -s 5 -countsPC '20' -bp 3
EVAL:
	bash compare_results.sh