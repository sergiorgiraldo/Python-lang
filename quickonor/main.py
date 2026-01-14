from itertools import combinations
import z3


def solve_paired_operations(output_numbers, known_slots=None):
    # puzzles can be 4,6,8
    how_many = len(output_numbers)

    solver = z3.Optimize()

    slots = [z3.Int(f"slot_{i}") for i in range(how_many)]

    if known_slots:
        for i, val in known_slots.items():
            solver.add(slots[i] == val)

    # Slots in increasing order
    for i in range(how_many - 1):
        solver.add(slots[i] <= slots[i+1])

    # Reasonable bounds
    for slot in slots:
        solver.add(slot >= 1, slot <= max(output_numbers))

    # All possible pairs
    all_pairs = list(combinations(range(how_many), 2))

    # Select exactly 4 pairs
    selected_pairs = [z3.Int(f"pair_{i}") for i in range(how_many // 2)]

    # Must use all slots
    for pair in selected_pairs:
        solver.add(pair >= 0, pair < len(all_pairs))
    solver.add(z3.Distinct(selected_pairs))

    # For each of the pairs, assign which outputs they produce (add and mul)
    output_assignment = [z3.Int(f"output_{i}") for i in range(how_many)]
    solver.add(z3.Distinct(output_assignment))
    for output in output_assignment:
        solver.add(output >= 0, output < how_many)

    # Match operations to outputs
    for pair_idx in range(how_many // 2):
        add_out_idx_var = output_assignment[pair_idx * 2]
        mul_out_idx_var = output_assignment[pair_idx * 2 + 1]

        # For each possible pair selection, add constraints
        for possible_pair_idx, (i, j) in enumerate(all_pairs):
            # For each possible output assignment
            for add_out in range(how_many):
                for mul_out in range(how_many):
                    if add_out != mul_out:  # Must assign to different outputs
                        solver.add(z3.Implies(
                            z3.And(
                                selected_pairs[pair_idx] == possible_pair_idx,
                                add_out_idx_var == add_out,
                                mul_out_idx_var == mul_out
                            ),
                            z3.And(
                                slots[i] + slots[j] == output_numbers[add_out],
                                slots[i] * slots[j] == output_numbers[mul_out]
                            )
                        ))

    # Solve
    if solver.check() == z3.sat:
        model = solver.model()
        slot_values             = [model.evaluate(slots[i]).as_long() 
                                    for i in range(how_many)]
        selected_pair_indices   = [model.evaluate(selected_pairs[i]).as_long() 
                                    for i in range(how_many // 2)]
        used_pairs              = [all_pairs[i] 
                                    for i in selected_pair_indices]
        out_assign              = [model.evaluate(output_assignment[i]).as_long()
                                    for i in range(how_many)]

        result = {
            "slots": slot_values,
            "pairs": []
        }
        for pair_idx in range(how_many // 2):
            i, j = used_pairs[pair_idx]
            add_out = out_assign[pair_idx * 2]
            mul_out = out_assign[pair_idx * 2 + 1]

            result["pairs"].append({
                "slot_indices": (i, j),
                "slot_values": (slot_values[i], slot_values[j]),
                "add": {
                    "result": slot_values[i] + slot_values[j],
                    "target": output_numbers[add_out],
                    "output_index": add_out
                },
                "multiply": {
                    "result": slot_values[i] * slot_values[j],
                    "target": output_numbers[mul_out],
                    "output_index": mul_out
                }
            })

        return result
    else:
        return None


if __name__ == "__main__":
    outputs = [40,56,64,104,300,399,400, 495]
    known = {2: 7, 6: 57}

    print("Solving for outputs:", outputs)
    print("Known slots:", known if known else "None")
    print()

    solution = solve_paired_operations(outputs, known)

    if solution:
        print('Solution found!')
        print(f'\nInput slots: {solution["slots"]}')
        print('\nPairs and operations:')

        for idx, pair in enumerate(solution["pairs"], 1):
            si, sj = pair["slot_indices"]
            vi, vj = pair["slot_values"]
            print(f'\nPair {idx}: slots[{si}]={vi}, slots[{sj}]={vj}')
            print(
                f'  Add: {vi} + {vj} = {pair["add"]["result"]} → output[{pair["add"]["output_index"]}] = {pair["add"]["target"]}')
            print(
                f'  Mul: {vi} × {vj} = {pair["multiply"]["result"]} → output[{pair["multiply"]["output_index"]}] = {pair["multiply"]["target"]}')
    else:
        print("No solution found!")
