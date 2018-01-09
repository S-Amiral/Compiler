.sub main
	say "Start!"

	.local num a
	$N2 = 0.0
	a = $N2

	'abc' (5.0,10.0,15.0)

	WLOOP1:
	.local num b
	$N3 = 3.0
	b = $N3

	WLOOP2:
	say a

	if a == 5.0 goto COND1
	goto COND1_END
	COND1:
	'a' (b)

	COND1_END:
	$N4 = b - 1.0
	b = $N4

	if b >= 2.0 goto WLOOP2
	goto WLOOP2_DONE
	WLOOP2_DONE:

$N5 = a + 1.0
	a = $N5

	if a < 10.0 goto WLOOP1
	goto WLOOP1_DONE
	WLOOP1_DONE:

	.local num t
	$N6 = 1.0
	t = $N6

	.local num d
	$N8 = 1.0
	d = $N8

	FLOOP1:
	'void' ()

	$N7 = d * 2.0
	d = $N7

	if d <= 8.0 goto FLOOP1
	goto FLOOP1_DONE
	FLOOP1_DONE:

.end

.sub 'abc'
	.param num a
	.param num b
	.param num c
	.local num d
	$N1 = a * b
	d = $N1

	say d

	say b

	say c

.end

.sub 'a'
	.param num a
	say a

.end

.sub 'void'
	say 2000.0

	say "void executed"

.end
