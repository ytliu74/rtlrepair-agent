`timescale 1ns/1ps
module tb;
    reg clk = 0;
    reg reset = 1;
    reg wr_en = 0;
    reg rd_en = 0;
    reg [7:0] data_in = 0;
    wire [7:0] data_out;
    wire [4:0] count;
    wire full, empty;
    fifo dut(.*);
    always #5 clk = ~clk;

    // Independent shift-queue scoreboard, not the DUT's circular-buffer design.
    reg [7:0] queue [0:15];
    integer size = 0;
    reg [7:0] last_read = 0;
    integer checks = 0;
    integer cycles = 0;
    integer full_both = 0, empty_both = 0, both = 0;
    integer overflow = 0, underflow = 0, resets = 0;
    integer i, batch;
    reg [31:0] stimulus = 32'h598cafe1;

    task check_state;
        begin
            checks = checks + 1;
            if (count !== size[4:0] || full !== (size == 16) ||
                empty !== (size == 0) || data_out !== last_read) begin
                $display("TEST_FAIL cycle=%0d check=%0d expected_count=%0d got=%0d expected_data=%02h got=%02h full=%b empty=%b",
                         cycles, checks, size, count, last_read, data_out, full, empty);
                $fatal(1, "FIFO scoreboard mismatch");
            end
        end
    endtask

    task step;
        input r, w, rd;
        input [7:0] value;
        reg accept_read, accept_write;
        integer j;
        begin
            @(negedge clk);
            #1;
            check_state(); // No falling-edge changes.
            reset = r;
            wr_en = w;
            rd_en = rd;
            data_in = value;
            #1;
            check_state(); // Synchronous reset and registered data_out.
            @(posedge clk);
            cycles = cycles + 1;
            if (r) begin
                size = 0;
                last_read = 0;
                resets = resets + 1;
            end else begin
                accept_read = rd && size > 0;
                accept_write = w && (size < 16 || accept_read);
                if (size == 16 && w && rd) full_both = full_both + 1;
                if (size == 0 && w && rd) empty_both = empty_both + 1;
                if (accept_read && accept_write) both = both + 1;
                if (w && !accept_write) overflow = overflow + 1;
                if (rd && !accept_read) underflow = underflow + 1;
                if (accept_read) begin
                    last_read = queue[0];
                    for (j = 0; j < size - 1; j = j + 1) queue[j] = queue[j+1];
                    size = size - 1;
                end
                if (accept_write) begin
                    queue[size] = value;
                    size = size + 1;
                end
            end
            #1;
            check_state();
        end
    endtask

    initial begin
        @(posedge clk);
        #1;
        check_state();
        step(0, 0, 1, 0); // Underflow.
        step(0, 1, 1, 8'ha5); // Empty simultaneous requests: no bypass.
        step(0, 0, 1, 0);
        step(0, 0, 1, 0); // Empty must retain previous registered read value.
        for (i = 0; i < 16; i = i + 1) step(0, 1, 0, i + 8'h20);
        step(0, 1, 0, 8'hee); // Overflow must not corrupt queue contents.
        for (i = 0; i < 4; i = i + 1) step(0, 1, 1, i + 8'h80);
        for (i = 0; i < 16; i = i + 1) step(0, 0, 1, 0);
        // Repeated complete fills/drains exercise pointer wrap and byte ordering.
        for (batch = 0; batch < 5; batch = batch + 1) begin
            for (i = 0; i < 16; i = i + 1) step(0, 1, 0, batch * 17 + i);
            step(0, 0, 0, 8'hff); // Hold while nonempty.
            for (i = 0; i < 16; i = i + 1) step(0, 0, 1, 0);
        end
        for (i = 0; i < 7; i = i + 1) step(0, 1, 0, i + 8'hf0);
        step(1, 1, 1, 8'h55); // Reset priority while nonempty.
        step(0, 0, 1, 0); // Contents before reset are no longer readable.
        for (i = 0; i < 512; i = i + 1) begin
            stimulus = {stimulus[30:0], stimulus[31] ^ stimulus[21] ^ stimulus[1] ^ stimulus[0]};
            step(i % 73 == 72, stimulus[0], stimulus[1], stimulus[15:8]);
        end
        for (i = 0; i < 17; i = i + 1) step(0, 0, 1, 0);
        if (full_both == 0 || empty_both == 0 || both == 0 ||
            overflow == 0 || underflow == 0 || resets == 0) begin
            $display("TEST_FAIL missing directed coverage");
            $fatal(1, "coverage");
        end
        $display("Cycles: %0d; checks: %0d", cycles, checks);
        $display("Coverage: full_both=%0d empty_both=%0d both=%0d overflow=%0d underflow=%0d resets=%0d",
                 full_both, empty_both, both, overflow, underflow, resets);
        $display("TEST_PASS");
        $finish;
    end
    initial begin
        #20000;
        $display("TEST_FAIL watchdog timeout");
        $fatal(1, "timeout");
    end
endmodule
