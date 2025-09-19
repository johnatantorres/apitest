from fastapi import HTTPException, status


def user_not_found():
    """Raises HTTPException for user not found."""
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="User not found"
    )


def thread_not_found():
    """Raises HTTPException for thread not found."""
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Thread not found"
    )


def user_for_thread_not_found():
    """Raises HTTPException for user associated with a thread not found."""
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="User for this thread not found"
    )