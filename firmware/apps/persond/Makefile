CC ?= gcc
CFLAGS ?= -O2
CFLAGS += -Wall -Wextra -Werror -std=gnu11

all: persond

persond: persond.c persond_logic.c persond_logic.h
	$(CC) $(CFLAGS) -o $@ persond.c persond_logic.c $(LDFLAGS) -lmosquitto -ljson-c

test_logic: test_logic.c persond_logic.c persond_logic.h
	$(CC) $(CFLAGS) -o $@ test_logic.c persond_logic.c

test: test_logic
	./test_logic

clean:
	rm -f persond test_logic

.PHONY: all test clean
