protocol_selection_prompt = '''I will write a request to you.
It will contain a decentralized application name, like Uniswap or Opensea.
I want you to give me the decentralized application mentioned in the request.

Here is the request: %s

The decentralized application will be from one of the following options:
uniswap
balancer
usdc
decentraland
opensea
aave

Type only the decentralized application's name. Do not explain your answer.'''

query_prompt = '''On your following response, only show the code and do not use sentences.
Following is the schema for %s's subgraph.
Based on this schema, write me a query for the %s.
The query language is GraphQL.
I want you to give me only the code. Do not start with "here is ..." or do not end with "this query ..."

%s
'''
