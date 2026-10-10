# 71. Simplify Path
# https://leetcode.com/problems/simplify-path/
#
# Splitting on '/' makes every rule local to one component:
#
#   - "" (from a leading, trailing or doubled slash) and "." mean "stay put";
#   - ".." pops the last real directory, and popping an empty stack is a no-op,
#     which is what makes "/../" collapse to "/";
#   - anything else, including "..." and "....", is an ordinary name.
#
# The stack then holds exactly the canonical components, so joining them with a
# single leading slash produces the answer.
#
# Time: O(n)   Space: O(n)

class Solution:
    def simplifyPath(self, path: str) -> str:
        stack: list[str] = []

        for component in path.split('/'):
            if component == '' or component == '.':
                continue
            if component == '..':
                if stack:
                    stack.pop()
            else:
                stack.append(component)

        return '/' + '/'.join(stack)
