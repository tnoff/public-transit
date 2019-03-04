BART_MULTIPLE_STOP_SCHEMA = {
    "type" : "object",
    "properties" : {
        "/" : {},
    },
    "patternProperties" : {
        "^([a-z0-9]+)$" : {
            "type" : "array",
            "items" : {
                "type" : "string",
                "pattern" : "^([a-zA-Z0-9]+)$",
            },
        },
    },
}

NEXTBUS_MULTIPLE_STOP_SCHEMA = {
    "type" : "object",
    "properties" : {
        "/" : {},
    },
    "patternProperties" : {
        "^([a-z0-9]+)$" : {
            "type" : "array",
            "items" : {
                "type" : "string",
                "pattern" : "^([a-zA-Z0-9-_]+)$",
            },
            "minItems" : 1,
        },
    },
}
