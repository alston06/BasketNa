import { HttpAgent } from "@ag-ui/client";
import {
    CopilotRuntime,
    copilotRuntimeNodeHttpEndpoint,
    GoogleGenerativeAIAdapter,
} from "@copilotkit/runtime";
import { createServer } from "node:http";

const serviceAdapter = new GoogleGenerativeAIAdapter({ model: "" });

const server = createServer((req, res) => {
	const runtime = new CopilotRuntime({
		agents: {
			my_agent: new HttpAgent({
				url: "http://localhost:8000/copilotkit_remote",
			}), // Adjust the URL as needed
		},
	});
	const handler = copilotRuntimeNodeHttpEndpoint({
		endpoint: "/copilotkit",
		runtime,
		serviceAdapter,
	});

	return handler(req, res);
});

server.listen(4000, () => {
	console.log("Listening at http://localhost:4000/copilotkit");
});
