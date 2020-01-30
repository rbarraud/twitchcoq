#!/usr/bin/env python3

MS = 4
MAXS = 120

mss = -1
mst = -1

def mprint(m):
  # match https://catonmat.net/busy-beaver
  s = []
  for k,v in sorted(m.items()):
    s.append(k[0]+str(k[1])+" -> "+v[2]+str(v[0])+str(v[1]))
  return ' '.join(s)
  
def run(M, s, t, h, steps):
  global mss, mst
  # step count or head escape to end
  while steps < MAXS and h > 1 and h < len(t)-1:

    # state adder, kick off with recursion
    if s not in M:
      # this fixes 4
      nsp = [chr(ord('a')+i) for i in range(MS)] + ['H']
      """
      # jump to all current states possible
      nsp = sorted(list(set([k[0] for k in M])))
      if len(nsp) < MS:
        # not at the limit, add one more state
        nsp.append(chr(ord('a')+len(nsp)))
      else:
        # seen all, now we can halt
        nsp.append('H')
      """
      #print("missing", s)
      for w in [0, 1]:
        for d in ['l', 'r']:
          for ns in nsp:
            # copy M and t here, and kick off all the new machines
            Mp = M.copy()
            Mp[s] = (w,d,ns)
            #print(mprint(Mp))
            run(Mp, s, t[:], h, steps)

      # this machine was incomplete, don't keep running
      return

    # s in M
    w,d,ns = M[s]

    # update the tape and head position
    t[h] = w
    if d == 'l':
      h -= 1
    else:
      h += 1

    s = (ns, t[h])
    steps += 1

    # check for halt
    if s[0] == 'H':
      mss = max(steps, mss)
      mst = max(sum(t), mst)
      print("halt", steps, sum(t), mss, mst) #, mprint(M))
      break
    


t = [0]*(MAXS*2)
M = {}
M[('a', 0)] = (1, 'r', 'b')
run(M, ('a', 0), t, MAXS, 0)
print(mss, mst)


