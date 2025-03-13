# Senior Data Engineering - Take home task

Objective: Construct a local data pipeline consuming [Bluesky](https://bsky.app/) event streams.

### Input

As an input, the pipeline will leverage the `./bluesky` script, which will output to stdout a stream of bluesky events, in JSON format.

:warning: [`uv`](https://docs.astral.sh/uv/getting-started/installation/) is required to run the `./bluesky` script.

If you don't know Bluesky product - you can see it as a twitter clone. Users will create "posts" - and other users can "like" them.

It is _not_ expected that you have any understanding of bluesky or the underlying technologies whatsoever. You should _not_ interact with bluesky API directly - you will only consume the events produced by the `./bluesky` script.

Relevant event shapes (partial):

```ts
// like event
{
  timestamp: string,
  action: "create",
  path: `app.bsky.feed.like/${id}`,
  repo: string, // the id of the user liking the post
  record: {
    uri: string, // the uri of the liked post
    // ...
  }
  // ...
}

// post event
{
  timestamp: string,
  action: "create",
  path: `app.bsky.feed.post/${postId}`,  // include the post id
  repo: string,  // the id of the user creating the post
  record: {
    text: string,
    langs: Array<string>,
    // ...
  },
  // ...
}
```

### Output

As an output, the pipeline will generate and keep up to date a few metrics (as CSV files):

- `./metrics/likes-per-minutes.csv`: time evolution: number of likes over time (minute by minute).
- `./metrics/fast-likers.csv`: fast liker: the list of all users who liked at least 50 posts in less than a minute.
- `./metrics/top-10-word.csv`: the list of the top 10 meaningful words used in posts that contain the word "engineering".
- another metric of your choice. Please document the choice of this metric.

Here is an example of the expected output format for the `likes-per-minutes.csv` file:

```csv
time,likes
2025-03-10 17:54:00,52985
2025-03-10 17:55:00,54736
2025-03-10 17:56:00,54736
```

or the `fast-likers.csv` file:

```csv
user_id,likes
did:plc:xaul3dllodzwvyzqf44ah4fm,898
did:plc:vjz25msr2f7izosxkro6ys55,886
did:plc:ifdj5n6n5hhmsq7udsrmckfi,760
did:plc:eh3fen366rkkf7mziyjm35d6,634
```

### Pipeline requirements

- the pipeline should be implemented primarly in python / SQL.
- you are allowed to use any (open source) external library / database you want; however, please ensure that the pipeline setup does not become overly complex for our team.
- your submission should include one or two executable files:
  - a `handle-stream` executable file that will accept bluesky events via stdin
    - we will run `./bluesky | ./handle-stream`
  - (optional) a `periodic` executable file that will be executed periodically
    - we will run `watch -n 30 ./periodic`
- Your pipeline needs to output the metrics as CSV files
  - in the `metrics/` folder.
  - No postprocessing / aggregations should be needed on the files.
  - There's no need to build anything on the visualization side, the CSVs are enough. We'll inspect the files themselves as well as the output of `cat metrics/[metric].csv | uplot bar -d, -H`.

## What you should do

- Implement the pipeline
- Include a README.md file with instructions for running the pipeline, as well as an explanation of your approach, your choices, and their limitations.
- Submit your code (ideally as a git bundle file or a GitHub link). There is no need to include any data, we will run the pipeline with real data.
- We are not looking for production-ready code, and we are aware of the limitations of this exercise. The main goal is to see how you approach a problem and write code. That being said, we expect candidates to use this exercise as an opportunity to demonstrate the concepts that are important to them in production, underline the tradeoffs they made, and explain what they would do differently in a production setting.
- This challenge should take about 2 to 3 hours of work. It's okay if you don't finish everything: it's all about tradeoffs.
