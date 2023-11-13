function describe(name, func)
{
	console.log("<DESCRIBE::>"+name)
	var before = performance.now()
	func()
	time = performance.now() - before
	console.log("<COMPLETEDIN::>" + parseFloat(time).toFixed(2))
}
function it(name, func)
{
	var before = performance.now()
	console.log("<IT::>"+name)
	try {
		func()
		console.log("<PASSED::>" + name)
	} catch (error) {
		console.log("<FAILED::>" + error.message)
	}
	time = performance.now() - before
	console.log("<COMPLETEDIN::>" + parseFloat(time).toFixed(2))
}
