import { type RouteConfig, index, route } from "@react-router/dev/routes";

export default [
    index("routes/home.tsx"),
    route("/encrypt", "routes/encrypt.tsx"),
    route("/decrypt", "routes/decrypt.tsx"),
    route("/*", "routes/404.tsx")
] satisfies RouteConfig;
