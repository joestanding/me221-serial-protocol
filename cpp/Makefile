# Define the compiler
CXX=g++

# Define any compile-time flags
CXXFLAGS=-Wall -g

# Define the source files
SOURCES=tests.cpp me.cpp

# Define the object files
OBJECTS=$(SOURCES:.cpp=.o)

# Define the executable file
EXECUTABLE=tests

all: $(SOURCES) $(EXECUTABLE)

$(EXECUTABLE): $(OBJECTS)
	$(CXX) $(OBJECTS) -o $@

.cpp.o:
	$(CXX) $(CXXFLAGS) -c $< -o $@

test: $(EXECUTABLE)
	./$(EXECUTABLE)

clean:
	rm -f $(OBJECTS) $(EXECUTABLE)

