CC ?= gcc
CFLAGS ?= -O2
CFLAGS += -Wall -Wextra -Werror -std=gnu11

all: daynight

daynight: daynight.c daynight_logic.c daynight_logic.h
	$(CC) $(CFLAGS) -o $@ daynight.c daynight_logic.c $(LDFLAGS)

test_logic: test_logic.c daynight_logic.c daynight_logic.h
	$(CC) $(CFLAGS) -o $@ test_logic.c daynight_logic.c -lm

test: test_logic
	./test_logic

clean:
	rm -f daynight test_logic

.PHONY: all test clean
