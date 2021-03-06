# twitchcoq -- a backspace.ai project

Reimplementing a subset of Coq in Python. 

Just kidding, Coq is too complex. We implemented metamath instead.

It (slowly) verifies set.mm as of 11/3/2019

Ideally, Coq and friends should be rewritten in metamath. It's really the future, just wish it looked better. But omg, this is the proper stack for formal math, "formalism" is alive and well and is the truth in philosophy.

# metamath as execution

We should be able to "run" a metamath program, aka proof without the target. It's a stack machine. The interpreter is only verifying that the proof is a valid program trace for the machine.

# metamath on search

Take set.mm, remove all $p definitions. Find them with search. Powered by AI(tm).

"metasmash" written in C++17. First with the intermediate nodes in the graph. Then make it sparser. Then remove it altogether.

How many of the 71 Metamath theorems can we rediscover without the scaffolding?

Hmm, https://github.com/dwhalen/holophrasm

# random notes

First order logic:

<pre>
Theorem test : exists x : nat, x + 2 = 4.
Theorem test2 : forall y : nat, (exists x : nat, x = y).
</pre>

Second order logic (quantifing over first order logic statements):

<pre>
forall y : (fun x : nat -> nat)
</pre>

Higher order logic...so on and so forth

# randomer notes

Imagine twitch, but VR. We'll rebuild the cybercafes, the revolutionary coffee shops, the old hacker spaces, the town square, the churches, all of the trappings of civilization. But we'll build them in machines. We'll build them in math. We'll build them in homomorphically encrypted lockers. We'll build them where copies are free, tax is ridiculous, removing your landlord is a fork, and the only axis on which to compete is quality. True freedom of association.

We need embodiment to be free from the tyranny of owned space. And we need formalization to be secure.

The attacker vs defender battle may have been lost IRL. But in the world of information, the defender seems to win.

# thoughts

To build a machine that can program.

* How much of programming exists without real world context?
* Refactoring definitely is, optimizing for some notion of "readability".
* Speed definitely is, optimizing for well, speed.

metamath is just the program trace of a proof. Any language can be built on top of it to generate the trace.

Instead of proving two programs the same, can we prove two program traces the same? Depends on how we define the same, in the metamath sense, it's only the output at the end, aka easy.

Hehe, a program is just the compression of all of its traces. QIRA is AI lah 

# compression aside

Lossy compression has no meaning, though there is something aside from lossless compression. There's task specific compression, dealt with this at comma. The trees on the side of the road have no effect on the driving problem, and that's why a straight up lossless compressor isn't the goal function.

I think "Value Prediction Networks" (https://arxiv.org/abs/1707.03497) gets this right, would be fun to implement that. Correct to say you are just compressing to predict the reward?

Then there's the universal goal function of compression progress (https://arxiv.org/abs/0812.4360) as a way of separating noise (which will never be compressed), from signal (which will have a gradient of compression).


