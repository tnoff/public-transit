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
                "pattern" : "^([a-z0-9]+)$",
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
                "pattern" : "^([a-z0-9]+)$",
            },
            "minItems" : 1,
        },
    },
}
