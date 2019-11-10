#!/usr/bin/env python3
from __future__ import print_function
import os
import sys
import code
import lark
path = os.path.dirname(os.path.abspath(__file__))

l = lark.Lark(open(os.path.join(path, "mm.g")).read(), parser="lalr")
p = l.parse(open(os.path.join(path, "miu2.mm") if len(sys.argv)==1 else sys.argv[1]).read())
print("*********** LOADED ***********")

class Scope(object):
  def __init__(self):
    self.constants = set()
    self.asserts = dict()
    self.hypos = dict()
    self.variables = list()
    self.horder = list()
    self.vtypes = dict()
    self.disjoints = set()
    self.essen = list()

  def child(self):
    ret = Scope()
    # asserts are noscope
    ret.asserts = self.asserts

    ret.constants = self.constants.copy()
    ret.variables = self.variables[:]
    ret.horder = self.horder[:]
    ret.vtypes = self.vtypes.copy()
    ret.disjoints = self.disjoints.copy()

    ret.hypos = self.hypos.copy()
    ret.essen = self.essen[:]

    return ret

def lp(ms):
  return ' '.join(map(str, ms))

class Stack(object):
  def __init__(self):
    self.ss = []

  def __len__(self):
    return len(self.ss)

  def push(self, tyc, ms):
    self.ss.append((tyc, ms))
    print("*** pushed", tyc, lp(ms))

  def pop(self):
    ret = self.ss.pop()
    print("*** popped", ret[0], lp(ret[1]))
    return ret

  def peek(self):
    return self.ss[-1]

def variables_in_scope(scope, ms):
  tvars = []
  for e in scope.essen:
    for v in e['ms']:
      if v in scope.variables and v not in tvars:
        tvars.append(v)
  for v in ms:
    if v in scope.variables and v not in tvars:
      tvars.append(v)
  return sorted(tvars, key=lambda x: scope.horder.index(x))

def decompress_proof(scope, inms, children):
  crib = []
  for v in variables_in_scope(scope, inms):
    for lbl,kk in scope.hypos.items():
      if kk['ms'] == [v] and kk['floating']:
        if lbl not in crib:
          crib.append(lbl)

  # get essential hypothesis
  crib += [x['lbl'] for x in scope.essen]
  print(lp(crib))

  # add to crib and parse weird numbers
  cc = []
  for x in children:
    if x.type == "LABEL":
      crib.append(x)
    else:
      assert x.type == "COMPRESSED_PROOF_BLOCK"
      cc.append(str(x))

  # parse weird numbers
  nn = []
  zz = []
  acc = 0
  for c in ''.join(cc):
    if c in 'UVWXY':
      acc *= 5
      acc += ord(c) - (ord('U')-1)
    elif c in 'ABCDEFGHIJKLMNOPQRST':
      acc *= 20
      acc += ord(c) - (ord('A')-1)
      nn.append(acc)
      acc = 0
    elif c == "Z":
      assert acc == 0
      zz.append(len(nn))
  #print(len(crib), len(zz))
  ret = []
  for n in nn:
    i = n-1
    if i < len(crib):
      ret.append(crib[i])
    elif i < len(crib)+len(zz):
      z = zz[i-len(crib)]
      ret.append(z)
    else:
      print("out of range", i)
      assert False
    #print(len(ret), n, ret[-1])
  return ret

def verify_proof(scope, intyc, inms, xx):
  xx = xx.children[0]
  if xx.data == "compressed_proof":
    lbls = decompress_proof(scope, inms, xx.children)
  else:
    lbls = xx.children
  print(lp(lbls))
  refs = []
  stack = Stack()
  for ii, s in enumerate(lbls):
    sys.stdout.write("  proof(%d) %s -> " % (ii+1, s))
    bindings = {}
    def do_bind(scope, v):
      if v not in bindings:
        vt, vnms = stack.pop()
        assert v in scope.vtypes
        assert scope.vtypes[v] == vt
        print("  bind %s to %s" % (v, lp(vnms)))
        bindings[v] = vnms

    def bind(scope, ms):
      nms = []
      for v in ms:
        if v in scope.variables:
          # late binding no longer supported
          assert v in bindings
          nms.append(bindings[v])
        else:
          # pass through constants
          if v not in scope.constants:
            print("WTF", v, "ISN'T A CONSTANT", lp(ms))
          assert v in scope.constants
          nms.append([v])
      ret = []
      for x in nms:
        ret += x
      return ret

    if s in scope.asserts:
      a = scope.asserts[s]
      ms = a['ms']
      # first bind in essential scope
      pop = []

      for e in a['scope'].essen[::-1]:
        et, enms = stack.pop()
        print("%s: must verify %s %s is %s %s" % (e['lbl'], e['type'], lp(e['ms']), et, lp(enms)))
        assert e['type'] == et
        pop.append((et, enms, e['ms'], e['lbl']))

      # early binding
      tvars = variables_in_scope(a['scope'], ms)
      print("binding [%s]" % lp(tvars))
      for v in tvars[::-1]:
        do_bind(a['scope'], v)

      # verify disjoints
      for v1, v2 in a['scope'].disjoints:
        if v1 in bindings and v2 in bindings:
          for bvv1 in [x for x in bindings[v1] if x in a['scope'].variables]:
            for bvv2 in [x for x in bindings[v2] if x in a['scope'].variables]:
              # confirm bvv1 and bvv2 are disjoint in current scope
              print("verify %s %s disjoint" % (bvv1, bvv2))
              assert bvv1 != bvv2
              assert (bvv1, bvv2) in scope.disjoints or \
                     (bvv2, bvv1) in scope.disjoints

      # parse essential
      for et, enms, ems, lbl in pop:
        print("working on %s" % lbl)
        nms = bind(a['scope'], ems)
        print("compare %s to %s" % (lp(nms), lp(enms)))
        assert nms == enms

      stack.push(a['type'], bind(a['scope'], ms))
    elif s in scope.hypos:
      a = scope.hypos[s]
      # don't bind variables
      stack.push(a['type'], a['ms'])
    elif type(s) == int:
      oot, ooms = refs[s-1]
      print("load ref", s, oot, lp(ooms))
      stack.push(oot, ooms)
    else:
      raise Exception("%s label not found" % s)
    refs.append(stack.peek())

  # confirm stack is this
  o = stack.pop()
  print("  produced %s %s expected %s %s" % (o[0], lp(o[1]), intyc, lp(inms)))
  assert(len(stack) == 0)
  assert o == (intyc, inms)

def parse_stmt(scope, xx):
  if xx.data == "variable_stmt":
    for y in xx.children:
      vname = y.children[0]
      assert vname not in scope.variables
      scope.variables.append(vname)
  elif xx.data == "hypothesis_stmt":
    xx = xx.children[0]
    lbl = xx.children[0]
    tyc = xx.children[1].children[0].children[0]
    assert tyc in scope.constants
    if xx.data == "floating_stmt":
      var = xx.children[2].children[0]
      assert var in scope.variables
      # TODO: we are throwing away this name, do we need it?
      assert var not in scope.vtypes
      scope.vtypes[var] = tyc
      scope.hypos[lbl] = {"type": tyc, "ms": [var], "floating": True}
      scope.horder.append(var)
    elif xx.data == "essential_stmt":
      ms = xx.children[2:]
      scope.essen.append({"type": tyc, "ms": ms, "lbl": lbl})
      scope.hypos[lbl] = {"type": tyc, "ms": ms, "floating": False}
  elif xx.data == "assert_stmt":
    xx = xx.children[0]
    lbl = xx.children[0]
    tyc = xx.children[1].children[0].children[0]
    assert tyc in scope.constants
    if xx.data == "axiom_stmt":
      ms = xx.children[2:]
      proof = None
    elif xx.data == "provable_stmt":
      ms = xx.children[2:-1]
      proof = xx.children[-1]
    scope.asserts[lbl] = {'type': tyc, 'ms': ms, 'scope': scope.child(), 'proof': proof}
  elif xx.data == "disjoint_stmt":
    # if we don't check this, it should still verify, just sometimes wrongly
    av = [x.children[0] for x in xx.children]
    for v1 in av:
      assert v1 in scope.variables
      for v2 in av:
        if v1 != v2 and (v1,v2) not in scope.disjoints and (v2,v1) not in scope.disjoints:
          scope.disjoints.add((v1, v2))
  elif xx.data == "block":
    tscope = scope.child()
    for y in xx.children:
      parse_stmt(tscope, y.children[0])
  else:
    print("IMPLEMENT", xx.data)
    pass

scope = Scope()
for x in p.children:
  xx = x.children[0]
  if xx.data == "constant_stmt":
    for y in xx.children:
      cname = y.children[0]
      assert cname not in scope.constants
      scope.constants.add(cname)
  else:
    xx = xx.children[0]
    parse_stmt(scope, xx)

print("*********** PARSED ***********")
for k,v in scope.asserts.items():
  if v['proof'] is not None:
    print("******** verify %s" % k)
    verify_proof(v['scope'], v['type'], v['ms'], v['proof'])
print("*********** VERIFIED ***********")

