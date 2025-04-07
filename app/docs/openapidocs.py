from pydantic import BaseModel


class ErrorResponse(BaseModel):
    message: str


# POST /data-a documentation
data_a_post_summary = "Save Data A and merge with Data B"
data_a_post_description = (
    "This endpoint allows saving Data A, after which it triggers a merge with Data B "
    "and saves the merged data as Data C."
)
data_a_post_tags = ["Data Management"]
data_a_post_responses = {
    200: {
        "description": "Successfully saved data A and merged data",
        "content": {"application/json": {"example": {"status": "ok"}}},
    },
    500: {
        "model": ErrorResponse,
        "description": "Internal server error, please contact support.",
    },
}

# GET /data-c documentation
data_c_get_summary = "Retrieve Data C"
data_c_get_description = "This endpoint retrieves the merged Data C, which is the combination of Data A and Data B."
data_c_get_tags = ["Data Management"]
data_c_get_responses = {
    200: {
        "description": "Successfully retrieved Data C",
    },
    404: {
        "description": "Data C not available",
        "content": {
            "application/json": {"example": {"detail": "DATA C not available"}}
        },
    },
    500: {
        "model": ErrorResponse,
        "description": "Internal server error, please contact support.",
    },
}
