


function pell(n) {
	// input n is a Number
	// your smart code here
	return 0n; // return a BigInt
}

describe("Tests suite", function() {
	const { strictEqual } = require('chai').assert;

	function doTest(n, expected) {
		const actual = pell(n);
		strictEqual(actual, expected, `for n = ${n}\n`);
	}

	it("sample tests", function() {
		doTest(0, 0n);
		doTest(1, 1n);
		doTest(2, 2n);
		doTest(3, 5n);
		doTest(4, 12n);
		doTest(100, 66992092050551637663438906713182313772n);
	});
});
