Trong số các lớp con của Collaborator được hiển thị ở Hình 6.2, Moderator được mô hình hóa dưới dạng một Value Object (đối tượng giá trị). Các thể hiện (instances) được tạo tĩnh và liên kết với một Forum Aggregate (cụm thực thể Diễn đàn), điểm mấu chốt ở đây là giảm thiểu tối đa tác động mà nhiều Aggregate ở Context thượng nguồn (upstream Identity and Access Context - Ngữ cảnh Định danh và Truy cập), vốn sở hữu rất nhiều thuộc tính, có thể gây ra cho Collaboration Context (Ngữ cảnh Cộng tác). Chỉ với một vài thuộc tính riêng, Moderator đã mô hình hóa một khái niệm cốt lõi của Ubiquitous Language (ngôn ngữ chung / ngôn ngữ toàn hiện) được sử dụng trong Collaboration Context. Hơn nữa, lớp Moderator không chứa bất kỳ thuộc tính đơn lẻ nào từ Role Aggregate. Thay vào đó, chính tên lớp đã thể hiện vai trò Moderator mà người dùng đảm nhận. Bằng việc chủ động lựa chọn thiết kế này, Moderator là một thể hiện Value được tạo tĩnh và không nhằm mục đích giữ đồng bộ với Context nguồn ở xa. Bản hợp đồng chất lượng dịch vụ (quality-of-service contract) được cân nhắc kỹ lưỡng này đã trút bỏ một gánh nặng tiềm tàng cho Context tiêu thụ (consuming Context).

Dĩ nhiên, cũng có những lúc một đối tượng trong Context hạ nguồn (downstream Context) phải đạt trạng thái eventual consistency (nhất quán cuối cùng) với một phần trạng thái của một hoặc nhiều Aggregate ở Context từ xa. Trong trường hợp đó, chúng ta sẽ thiết kế một Aggregate ở Context tiêu thụ hạ nguồn, bởi vì các Entity (thực thể) được dùng để duy trì một chuỗi liên tục các thay đổi (thread of continuity of change). Tuy nhiên, chúng ta nên cố gắng tránh lựa chọn mô hình hóa này nếu có thể. Bất cứ khi nào có thể, hãy chọn Value Object để mô hình hóa các tích hợp. Lời khuyên này có thể áp dụng trong nhiều trường hợp khi tiêu thụ các Standard Type (kiểu chuẩn) từ xa.

Hình 6.2 Hệ thống phân cấp lớp Collaborator của các Value Object. Chỉ một vài thuộc tính của User được giữ lại từ Context thượng nguồn, với tên lớp làm rõ ràng các vai trò.

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000242_135adaa14e34cf34fc2e92829b576f777ee78938339b78dc4e5834bee3104607.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000243_ab9fe3ac36204f699ab9d1001cd9ebff5916eb4812e4d3a2f2a33bf45963e133.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000244_ec3a5fa9f293d8dec8c0262ea1b2e825ecdfef17fff5d1d89302f2c348e3ff69.png)

## Standard Types Expressed as Values

Trong nhiều hệ thống và ứng dụng, luôn tồn tại nhu cầu về thứ mà tôi gọi là Standard Types (các kiểu chuẩn). Standard Types là các đối tượng mô tả biểu thị cho các phân loại của sự vật. Luôn có chính sự vật đó (Entity) hoặc phần mô tả (Value), đồng thời cũng có các Standard Types để phân biệt chúng với các phân loại khác của cùng sự vật. Tôi không rõ tên gọi chuẩn của ngành cho khái niệm này là gì, nhưng tôi cũng từng nghe người ta gọi nó là một type code (mã loại) hay một lookup (bảng tra cứu). Cái tên type code không nói lên được nhiều điều. Còn lookup thì là tra cứu của cái gì? Tôi thích cái tên Standard Types hơn vì nó mang tính mô tả rõ ràng hơn. Để làm rõ khái niệm này, hãy xem xét một vài trường hợp sử dụng. Trong một số trường hợp, chúng được mô hình hóa dưới dạng Power Types (kiểu siêu hình / kiểu phân loại cấp cao).

> 💡 **Giải thích thêm:** *Power Type* là một mẫu thiết kế phân tích (do James Martin và James Odell khởi xướng, được Martin Fowler phổ biến trong tài liệu mô hình phân tích), trong đó một đối tượng biểu diễn một loại/phân loại của các đối tượng khác, cho phép hệ thống mở rộng hoặc thay đổi các loại thực thể linh hoạt tại thời điểm chạy mà không cần sửa cấu trúc lớp kế thừa.
> Nguồn tham khảo: [Martin Fowler - Power Type](https://martinfowler.com/apsupp/powerType.pdf)

Ubiquitous Language của bạn định nghĩa một PhoneNumber (Value), và nó cũng đòi hỏi bạn phải mô tả loại của từng số điện thoại. Chuyên gia nghiệp vụ (domain expert) của bạn hỏi: "Số điện thoại này là số nhà riêng, di động, cơ quan, hay loại khác?". Liệu các loại số điện thoại khác nhau có nên được mô hình hóa thành một hệ thống phân cấp lớp (class hierarchy) không? Việc tạo một lớp riêng cho từng loại sẽ khiến các client (phía gọi mã nguồn) khó phân biệt giữa chúng hơn. Ở đây, nhiều khả năng bạn sẽ muốn dùng một Standard Type để mô tả loại điện thoại, có thể là Home, Mobile, Work, hoặc Other. Những phần mô tả này đại diện cho các Standard Types của điện thoại.

Như tôi đã thảo luận trước đây, trong một miền nghiệp vụ tài chính, hoàn toàn có khả năng xuất hiện một kiểu Currency (Value) để ràng buộc một MonetaryValue (giá trị tiền tệ) vào một số tiền thuộc một loại tiền tệ cụ thể trên thế giới. Trong trường hợp này, Standard Type sẽ cung cấp một Value cho từng loại tiền tệ trên thế giới: AUD, CAD, CNY, EUR, GBP, JPY, USD, v.v. Việc sử dụng một Standard Type ở đây giúp bạn tránh được các loại tiền tệ giả mạo/không hợp lệ. Mặc dù một loại tiền tệ không chính xác vẫn có thể bị gán nhầm cho MonetaryValue, nhưng một loại tiền tệ không tồn tại thì không thể nào được gán vào. Nếu sử dụng thuộc tính dạng chuỗi ký tự (string), bạn có thể đẩy mô hình vào trạng thái không hợp lệ. Hãy thử nghĩ xem từ sai chính tả `doolars` sẽ gây ra những rắc rối như thế nào.

Bạn cũng có thể đang làm việc trong lĩnh vực dược phẩm và thiết kế cho các loại thuốc có nhiều đường dùng thuốc (administration routes) khác nhau. Một loại thuốc cụ thể (Entity) có vòng đời dài và các thay đổi được quản lý theo thời gian — nó được hình thành ý tưởng, nghiên cứu, phát triển, thử nghiệm, sản xuất, cải tiến và cuối cùng là ngừng lưu hành. Bạn có thể quyết định quản lý các giai đoạn vòng đời này bằng Standard Types hoặc không. Những bước chuyển dịch vòng đời này hoàn toàn có lý do chính đáng để được quản lý trong một vài Bounded Context (ngữ cảnh giới hạn) khác nhau. Mặt khác, đường dùng thuốc chỉ định cho bệnh nhân của từng loại thuốc có thể được phân loại bằng các mô tả Standard Type, chẳng hạn như IV (tiêm tĩnh mạch), Oral (uống), hoặc Topical (dùng ngoài da).

Tùy thuộc vào mức độ chuẩn hóa, các kiểu này có thể chỉ được duy trì ở cấp độ ứng dụng, hoặc được nâng tầm quan trọng lên các cơ sở dữ liệu dùng chung của doanh nghiệp, hoặc có sẵn thông qua các cơ quan tiêu chuẩn quốc gia hoặc quốc tế.

Mức độ chuẩn hóa đôi khi có thể ảnh hưởng đến cách Standard Types được truy xuất và sử dụng bên trong một mô hình.

Chúng ta có thể xem những đối tượng này là các Entity vì chúng có vòng đời riêng trong một Bounded Context chuyên biệt, bản địa (native). Bất kể chúng được tạo ra và duy trì như thế nào bởi bất kỳ cơ quan tiêu chuẩn nào, nếu có thể, chúng ta nên nỗ lực xem chúng như các Value trong Context tiêu thụ của mình. Cách này hoạt động hiệu quả vì chúng đo lường và mô tả các phân loại của sự vật, mà các phép đo lường và mô tả thì tốt nhất nên được mô hình hóa thành Value. Hơn nữa, chẳng hạn một thể hiện của {IV} cũng hoàn toàn giống hệt như bất kỳ thể hiện nào khác của {IV}. Chúng rõ ràng có thể hoán đổi cho nhau, điều đó cũng có nghĩa là chúng có thể thay thế được và có thể áp dụng tính bằng nhau theo giá trị (Value equality). Do đó, nếu không cần phải duy trì tính liên tục của sự thay đổi qua vòng đời của các kiểu mang tính mô tả trong Bounded Context của bạn, hãy mô hình hóa chúng thành các Value.

Vì mục đích bảo trì, thông thường Standard Types sẽ cư trú nguyên bản (natively reside) trong một Context tách biệt với các mô hình tiêu thụ chúng. Ở đó, chúng là các Entity và có vòng đời lưu trữ bền vững (persistent life cycle) với các thuộc tính như `identity` (danh tính), `name` (tên) và `description` (mô tả). Cũng có thể có các thuộc tính khác, nhưng những thuộc tính vừa nêu là phổ biến nhất để sử dụng trong một Context tiêu thụ. Chúng ta thường chỉ sử dụng một thuộc tính duy nhất. Điều này tuân thủ mục tiêu tích hợp với sự tối giản (integrate with minimalism).

Để lấy một ví dụ rất đơn giản, hãy xem xét một Standard Type mô hình hóa một thành viên của một nhóm (group) mà ở đó tồn tại hai loại thành viên. Có thể có các thành viên là người dùng (user) và các thành viên bản thân chúng lại là các nhóm (các nhóm lồng nhau - nested groups). Enum trong Java này đại diện cho một cách để hỗ trợ một Standard Type:

```java
package com.saasovation.identityaccess.domain.model.identity;

public enum GroupMemberType {
    GROUP {
        public boolean isGroup() {
            return true;
        }
    },
    USER {
        public boolean isUser() {
            return true;
        }
    };

    public boolean isGroup() {
        return false;
    }

    public boolean isUser() {
        return false;
    }
}
```

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000245_0304db097907f8889611c813ca4b13a525d05ae30c34fbf88d2b09031397ad5d.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000246_6a8aeb6e1091a7b30f479b6703a8221851e93d6104f9c0925985320da681978b.png)

Một thể hiện Value của GroupMember được khởi tạo với một GroupMemberType cụ thể. Để minh họa, khi một User hoặc một Group được gán vào một Group, Aggregate được gán sẽ được yêu cầu tạo ra một GroupMember tương ứng với chính nó. Dưới đây là phần hiện thực phương thức `toGroupMember()` của lớp User:

```java
protected GroupMember toGroupMember() {
    GroupMember groupMember = new GroupMember(
        this.tenantId(),
        this.username(),
        GroupMemberType.USER); // standard type dạng enum

    return groupMember;
}
```

Việc sử dụng một enum trong Java là một cách rất đơn giản để hỗ trợ một Standard Type. Enum cung cấp một số lượng hữu hạn các Value được định nghĩa rõ ràng (trong trường hợp này là hai), rất nhẹ và theo quy ước nó sở hữu Side-Effect-Free Behavior (hành vi không gây tác dụng phụ). Nhưng phần mô tả bằng văn bản của Value nằm ở đâu? Có hai câu trả lời khả dĩ. Thông thường, không cần thiết phải cung cấp mô tả cho kiểu, mà chỉ cần tên của nó là đủ. Tại sao? Các mô tả bằng văn bản thường chỉ hợp lệ ở Tầng Giao diện Người dùng (User Interface Layer) (14) và có thể được cung cấp bằng cách ánh xạ tên kiểu với một thuộc tính hướng giao diện (view-centric property). Nhiều khi thuộc tính hướng giao diện này phải được bản địa hóa (như trong điện toán đa ngôn ngữ), khiến việc hỗ trợ nó trong mô hình trở nên không phù hợp. Thông thường, chỉ riêng tên của Standard Type đã là thuộc tính tốt nhất để sử dụng trong mô hình. Câu trả lời thứ hai là có các mô tả giới hạn được tích hợp ngay trong tên trạng thái enum là `GROUP` và `USER`. Bạn có thể xuất ra các tên mô tả bằng hành vi `toString()` của từng kiểu. Tuy nhiên, nếu cần thiết, văn bản mô tả của từng kiểu cũng có thể được mô hình hóa cùng.

Standard Type mẫu dạng enum trong Java này về bản chất cũng là một đối tượng State (mẫu trạng thái) [Gamma et al.] thanh lịch và gọn gàng. Ở phần dưới của phần khai báo enum có hai phương thức hiện thực hành vi mặc định cho tất cả các State: `isGroup()` và `isUser()`. Theo mặc định, cả hai phương thức này đều trả về `false`, đây là hành vi cơ bản thích hợp. Tuy nhiên, trong mỗi định nghĩa State, các phương thức được ghi đè (override) để trả về `true` khi phù hợp với State cụ thể của chúng. Khi trạng thái của Standard Type là `GROUP`, phương thức `isGroup()` được ghi đè để mang lại kết quả `true`. Khi trạng thái của Standard Type là `USER`, phương thức `isUser()` được ghi đè để mang lại kết quả `true`. Trạng thái thay đổi bằng cách thay thế giá trị enum hiện tại bằng một giá trị khác.

Enum này minh họa một số hành vi rất cơ bản. Việc hiện thực mẫu State có thể phức tạp hơn tùy theo nhu cầu của miền nghiệp vụ, bổ sung thêm nhiều hành vi chuẩn được từng State ghi đè và chuyên biệt hóa. Theo đúng thực tế, đây là một ví dụ về một kiểu Value có các trạng thái bị giới hạn trong một tập hợp hằng số được định nghĩa rõ ràng. Một ví dụ quan trọng là `BacklogItemStatusType`, cung cấp các trạng thái `PLANNED`, `SCHEDULED`, `COMMITTED`, `DONE`, và `REMOVED`. Tôi sử dụng cách tiếp cận Standard Type này xuyên suốt ba Bounded Context mẫu. Tôi thấy nó giúp giữ cho chúng đơn giản nhất có thể.

## State Pattern Considered Harmful?

Một số người cho rằng mẫu State (State pattern) là điều không mấy mong muốn. Một phàn nàn phổ biến là nhu cầu phải tạo ra một hiện thực trừu tượng cho từng hành vi mà kiểu đó hỗ trợ (hai phương thức ở cuối `GroupMemberType`), rồi sau đó phải ghi đè các hành vi đó khi một State nhất định cần cung cấp một hiện thực chuyên biệt. Trong Java, điều này thường đòi hỏi một lớp riêng (thường nằm trong một tệp riêng) cho kiểu trừu tượng và cho cả từng State. Dù thích hay không, đó chính là cách vận hành của mẫu State.

Tôi đồng ý rằng khi phải phát triển các lớp State riêng biệt — một lớp cho mỗi trạng thái duy nhất cộng với một kiểu trừu tượng — nó có thể trở thành một mớ hỗn độn cồng kềnh. Các hành vi riêng biệt trong từng lớp, có thể bị trộn lẫn với một số hành vi mặc định từ lớp trừu tượng, có thể dẫn đến sự phụ thuộc chặt chẽ (tight coupling) giữa các lớp con và làm giảm khả năng đọc hiểu giữa các kiểu. Gánh nặng này đặc biệt nặng nề nếu bạn có một số lượng lớn các State. Tuy nhiên, tôi nghĩ rằng việc sử dụng enum trong Java là một cách rất đơn giản và có thể là tối ưu hơn để sử dụng mẫu State nhằm tạo ra một tập hợp các Standard Type. Tôi tin rằng bạn sẽ có được những điểm tinh túy nhất của cả hai cách tiếp cận. Bạn có được một Standard Type rất đơn giản cùng một cách để tra vấn chuẩn đó về State hiện tại của nó. Điều này giữ cho hành vi có tính gắn kết (cohesive) với kiểu. Việc giới hạn hành vi của State sẽ giúp việc sử dụng trở nên thiết thực.

Nhưng vẫn có thể bạn không thích ngay cả cách hiện thực State đơn giản này, và mỗi người đều có quan điểm riêng.

Nếu bạn quyết định không thích dùng enum trong Java để hỗ trợ Standard Types, bạn luôn có thể sử dụng một thể hiện Value duy nhất cho mỗi kiểu. Tuy nhiên, nếu mối bận tâm của bạn chủ yếu là bạn không thích ý tưởng sử dụng mẫu State, bạn hoàn toàn có thể dùng một enum để hỗ trợ Standard Type một cách thanh lịch mà không cần phải nghĩ về nó như mẫu State. Dù sao thì tôi có thể là người đầu tiên gieo ý nghĩ "enum chính là State" vào đầu bạn. Nói như vậy để thấy rằng, vẫn có những giải pháp thay thế khác để hiện thực Standard Types ngoài các cách tiếp cận dùng enum và Value.

Như một giải pháp thay thế, bạn có thể sử dụng một Aggregate làm một Standard Type với một thể hiện của Aggregate cho mỗi kiểu. Hãy nghĩ kỹ trước khi vội vã làm theo cách này. Các kiểu chuẩn nhìn chung không nên được duy trì bên trong chính Bounded Context tiêu thụ chúng. Các Standard Type được sử dụng rộng rãi thông thường nên được duy trì trong một Context tách biệt với các bản cập nhật được lên kế hoạch rất cẩn thận gửi tới các bên tiêu thụ. Thay vào đó, bạn có thể chọn hiển thị các Aggregate Standard Type dưới dạng bất biến (immutable) trong các Context tiêu thụ. Nhưng hãy tự hỏi liệu một Entity bất biến thì theo định nghĩa có thực sự là một Entity hay không. Nếu bạn nghĩ là không, bạn nên cân nhắc mô hình hóa nó thành một Value Object bất biến dùng chung.

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000247_a20d3af92c177f7e2a09ea8d2fd08fb2338f1d39be3e04d20da22d56be8ef567.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000248_3bbc330703b1ab772ed61cf71814cbe8d2e0ec868f691edb4485a5ba88769042.png)

Một Value Object bất biến dùng chung có thể được lấy từ một kho lưu trữ bền vững (persistence store) ẩn. Đây là một lựa chọn khả thi nếu được lấy từ một Standard Type Service (Dịch vụ Kiểu Chuẩn) (7) hoặc Factory (Nhà máy) (11). Nếu áp dụng, bạn có thể nên có một Service hoặc Factory provider cho mỗi tập hợp Standard Type (một cho các loại số điện thoại, một cái khác cho các loại địa chỉ bưu điện, một cho các loại tiền tệ), như được mô tả trong Hình 6.3. Trong cả hai trường hợp, các hiện thực cụ thể của một Service hoặc Factory sẽ truy cập kho lưu trữ bền vững để lấy các Value dùng chung khi cần, nhưng các client sẽ không bao giờ biết rằng các Value đó được lưu trữ trong một cơ sở dữ liệu chuẩn. Việc sử dụng Service hoặc Factory để cung cấp các kiểu cũng cho phép bạn áp dụng một số chiến lược bộ nhớ đệm (caching) khả thi một cách dễ dàng và an toàn vì các Value là chỉ đọc (read-only) từ kho lưu trữ và bất biến trong hệ thống.

Sau cùng, tôi nghĩ tốt nhất là nên ưu tiên dùng enum cho Standard Types dù bạn có thực sự xem nó là một State hay không. Nếu bạn có nhiều thể hiện Standard Type khả dĩ trong một danh mục duy nhất, hãy xem xét việc sinh mã (code generation) để tạo ra enum. Chẳng hạn, một cách tiếp cận sinh mã có thể đọc qua tất cả các Standard Type hiện có trong kho lưu trữ bền vững tương ứng của chúng (system of record - hệ thống nguồn chân lý) và tạo ra một kiểu/trạng thái duy nhất cho mỗi dòng dữ liệu.

Nếu bạn quyết định sử dụng các Value Object kinh điển làm Standard Types, bạn có thể thấy hữu ích khi giới thiệu một Service hoặc Factory để tạo các thể hiện tĩnh khi cần. Điều này cũng có các động lực tương tự như đã thảo luận trước đó nhưng sẽ khác biệt trong cách hiện thực so với những cơ chế tạo ra các Value dùng chung. Trong trường hợp này, Service hoặc Factory của bạn sẽ cung cấp các thể hiện Value bất biến được tạo tĩnh của từng Standard Type riêng lẻ. Bất kỳ thay đổi nào đối với các thực thể cơ sở dữ liệu Standard Type bên dưới trong hệ thống nguồn chân lý sẽ không tự động được phản ánh trong các thể hiện biểu diễn đã được tạo tĩnh từ trước. Nếu bạn muốn giữ cho các thể hiện Value được tạo tĩnh như vậy đồng bộ với hệ thống nguồn chân lý, bạn sẽ cần cung cấp một giải pháp tùy chỉnh để tìm kiếm và cập nhật trạng thái của chúng trong mô hình của mình. Điều này có thể triệt tiêu tính hữu ích tiềm năng của cách tiếp cận này. ⁴ Do đó, ngay từ khi bắt đầu thiết kế, bạn có thể xác định rằng tất cả các Value Standard Type được tạo tĩnh như vậy sẽ không bao giờ được cập nhật trong Bounded Context tiêu thụ. Mọi yếu tố cạnh tranh (competing forces) đều phải được cân nhắc kỹ lưỡng.

Hình 6.3 Một Domain Service có thể được sử dụng để cung cấp các Standard Type. Trong trường hợp này, Service đi tới cơ sở dữ liệu để đọc trạng thái của một CurrencyType được yêu cầu.

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000249_b03ac73335b984f96922d50bb5a492b2a2856df64d4bb2cf95de891bb7697307.png)

## Testing Value Objects

Để nhấn mạnh tinh thần test-first (kiểm thử trước), trước tiên tôi sẽ trình bày các bài kiểm thử mẫu trước khi cung cấp phần hiện thực của Value Object. Các bài kiểm thử này thúc đẩy thiết kế của mô hình miền (domain model) bằng cách cung cấp các ví dụ về cách một client sẽ sử dụng từng đối tượng.

Áp dụng phong cách này, chúng ta không quá bận tâm đến việc giải quyết các khía cạnh khác nhau của unit testing (kiểm thử đơn vị), chứng minh cặn kẽ rằng mô hình hoàn toàn bất khả xâm phạm ở mọi góc độ. Thay vào đó, tại thời điểm này, mối quan tâm lớn hơn là chứng minh các đối tượng khác nhau trong mô hình miền sẽ được các client sử dụng như thế nào và những client đó có thể kỳ vọng điều gì khi sử dụng chúng. Điều cốt yếu là phải đứng từ góc nhìn của client khi thiết kế mô hình nhằm nắm bắt được các khái niệm thiết yếu. Nếu không, chúng ta có thể đang mô hình hóa từ góc nhìn của chính mình thay vì từ góc nhìn của nghiệp vụ.

## Best Sample Code

Dưới đây là một cách tư duy về phong cách kiểm thử này: Nếu chúng ta đang viết một cuốn sổ tay hướng dẫn sử dụng cho mô hình, chúng ta sẽ cung cấp các bài kiểm thử này như những đoạn mã mẫu thích hợp nhất cho việc các client nên sử dụng đối tượng miền cụ thể này như thế nào.

Điều này không có nghĩa là không nên phát triển các bài kiểm thử đơn vị. Tất cả các bài kiểm thử bổ sung nhằm giải quyết các tiêu chuẩn của đội ngũ phát triển đều nên và phải được viết. Tuy nhiên, có những động lực khác nhau cho từng loại kiểm thử. Kiểm thử đơn vị và kiểm thử hành vi (behavioral tests) đều có vị trí riêng của chúng, cũng như các bài kiểm thử mô hình hóa sau đây.

Value Object được chọn là một ví dụ đại diện toàn diện tốt, được trích xuất từ Core Domain (Miền Cốt Lõi) (2) mới nhất, đó là Agile Project Management Context (Ngữ cảnh Quản lý Dự án Agile).

⁴. Đây sẽ là thời điểm thích hợp để mô hình hóa một Aggregate ở Context thượng nguồn cũng thành một Aggregate ở Context hạ nguồn. Chúng sẽ không cùng một lớp hoặc nhất thiết phải chứa tất cả các thuộc tính giống nhau, nhưng việc mô hình hóa khái niệm hạ nguồn dưới dạng một Aggregate sẽ cho phép đạt được tính nhất quán cuối cùng và các cập nhật tại một điểm duy nhất.

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000250_46cfbf8f47960c971bbe7e887423b1e650fb0772f114066b3c6733fa3f4a4905.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000251_4a18c9aa6fbfb1d06a31b2bccbb423059e7c0fe2d9fad30f2418fafabafa4869.png)

Trong Bounded Context này, các chuyên gia nghiệp vụ nhắc đến 'mức độ ưu tiên nghiệp vụ của các hạng mục tồn đọng' (business priority of backlog items). Để đáp ứng phần này của Ubiquitous Language, chúng tôi mô hình hóa khái niệm này thành một `BusinessPriority`. Nó cung cấp đầu ra đã được tính toán phù hợp để hỗ trợ phân tích kinh doanh về giá trị của việc phát triển từng hạng mục tồn đọng của sản phẩm (product backlog item) [Wiegers]. Các đầu ra bao gồm tỷ lệ phần trăm chi phí (cost percentage) — tức là chi phí phát triển một hạng mục tồn đọng cụ thể so với chi phí phát triển tất cả các hạng mục khác; tổng giá trị (total value) — tức là tổng giá trị thu được bằng cách phát triển một hạng mục tồn đọng cụ thể; và phần trăm giá

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000252_0441b5b8050dc196d3f3e6fc5de4cfb8c00975ba517e848967dc2dbc6d692bb7.png)

trị (value percentage) — tức là giá trị phát triển một hạng mục tồn đọng cụ thể so với giá trị phát triển bất kỳ hạng mục nào khác; và mức độ ưu tiên (priority) — tức là mức độ ưu tiên đã tính toán mà nghiệp vụ nên cân nhắc dành cho hạng mục tồn đọng này khi so sánh với tất cả các hạng mục khác.

Những bài kiểm thử này thực chất đã xuất hiện qua nhiều vòng lặp tái cấu trúc (refactoring iterations) ngắn với các bước tinh chỉnh từng bước, mặc dù ở đây chúng được trình bày như một tập hợp hoàn chỉnh:

```java
package com.saasovation.agilepm.domain.model.product;

import com.saasovation.agilepm.domain.model.DomainTest;
import java.text.NumberFormat;

public class BusinessPriorityTest extends DomainTest {

    public BusinessPriorityTest() {
        super();
    }

    ...

    private NumberFormat oneDecimal() {
        return this.decimal(1);
    }

    private NumberFormat twoDecimals() {
        return this.decimal(2);
    }

    private NumberFormat decimal(int aNumberOfDecimals) {
        NumberFormat fmt = NumberFormat.getInstance();
        fmt.setMinimumFractionDigits(aNumberOfDecimals);
        fmt.setMaximumFractionDigits(aNumberOfDecimals);
        return fmt;
    }
}
```

Lớp này có một số hàm trợ giúp kiểm thử (fixture helpers). Vì nhóm cần kiểm tra độ chính xác của các phép tính toán khác nhau, họ đã viết các phương thức để cung cấp các thể hiện `NumberFormat` cho các giá trị phân số có một hoặc hai chữ số ở bên phải dấu thập phân. Bạn sẽ thấy ngay sau đây lý do tại sao chúng lại hữu ích:

```java
public void testCostPercentageCalculation() throws Exception {
    BusinessPriority businessPriority =
        new BusinessPriority(
            new BusinessPriorityRatings(2, 4, 1, 1));

    BusinessPriority businessPriorityCopy =
        new BusinessPriority(businessPriority);

    assertEquals(businessPriority, businessPriorityCopy);

    BusinessPriorityTotals totals =
        new BusinessPriorityTotals(53, 49, 53 + 49, 37, 33);

    float cost = businessPriority.costPercentage(totals);

    assertEquals(this.oneDecimal().format(cost), "2.7");
    assertEquals(businessPriority, businessPriorityCopy);
}
```

Nhóm đã nảy ra một ý tưởng hay để kiểm thử tính bất biến (immutability). Mỗi bài kiểm thử trước tiên tạo ra một thể hiện của `BusinessPriority`, sau đó tạo ra một bản sao tương đương của nó bằng cách sử dụng copy constructor (hàm khởi tạo sao chép). Khẳng định kiểm thử (assertion) đầu tiên trong bài test đảm bảo rằng hàm khởi tạo sao chép tạo ra một bản sao bằng với bản gốc.

Tiếp theo, họ thiết kế bài kiểm thử để tạo ra `BusinessPriorityTotals` và gán nó vào biến phương thức `totals`. Với `totals`, họ có thể sử dụng phương thức truy vấn `costPercentage()` và gán kết quả cho biến `cost`. Sau đó, họ khẳng định rằng giá trị được trả về là `2.7`, đây là kết quả chính xác được tính toán thủ công từ trước. Cuối cùng, họ khẳng định rằng hành vi của phương thức `costPercentage()` thực sự không gây ra tác dụng phụ (side-effect free), điều này sẽ đúng nếu `businessPriority` vẫn giữ nguyên tính bằng nhau theo giá trị với `businessPriorityCopy`. Từ bài kiểm thử này, họ đã nắm được cách tính toán tỷ lệ phần trăm chi phí và kết quả đầu ra của chúng sẽ như thế nào.

Tiếp theo, họ cần kiểm thử mức độ ưu tiên, tổng giá trị và các phép tính phần trăm giá trị, sử dụng cùng một kế hoạch triển khai cơ bản:

```java
public void testPriorityCalculation() throws Exception {
    BusinessPriority businessPriority =
        new BusinessPriority(
            new BusinessPriorityRatings(2, 4, 1, 1));

    BusinessPriority businessPriorityCopy =
        new BusinessPriority(businessPriority);
```

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000253_aad1f479aafe499fa6c6e7d5e67f01b67ad51fca95e1a2fb0961eecdead7863e.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000254_735b5bedd14202d8150b3010d14b27e711da17bf17e4b0f985815af7fb6b9d5c.png)

## Chapter 6 VALUE OBJECTS

```java
    assertEquals(businessPriorityCopy, businessPriority);

    BusinessPriorityTotals totals =
        new BusinessPriorityTotals(53, 49, 53 + 49, 37, 33);

    float calculatedPriority = businessPriority.priority(totals);

    assertEquals("1.03", this.twoDecimals().format(calculatedPriority));
    assertEquals(businessPriority, businessPriorityCopy);
}

public void testTotalValueCalculation() throws Exception {
    BusinessPriority businessPriority =
        new BusinessPriority(
            new BusinessPriorityRatings(2, 4, 1, 1));

    BusinessPriority businessPriorityCopy =
        new BusinessPriority(businessPriority);

    assertEquals(businessPriority, businessPriorityCopy);

    float totalValue = businessPriority.totalValue();

    assertEquals("6.0", this.oneDecimal().format(totalValue));
    assertEquals(businessPriority, businessPriorityCopy);
}

public void testValuePercentageCalculation() throws Exception {
    BusinessPriority businessPriority =
        new BusinessPriority(
            new BusinessPriorityRatings(2, 4, 1, 1));

    BusinessPriority businessPriorityCopy =
        new BusinessPriority(businessPriority);

    assertEquals(businessPriority, businessPriorityCopy);

    BusinessPriorityTotals totals =
        new BusinessPriorityTotals(53, 49, 53 + 49, 37, 33);

    float valuePercentage = businessPriority.valuePercentage(totals);

    assertEquals("5.9", this.oneDecimal().format(valuePercentage));
    assertEquals(businessPriorityCopy, businessPriority);
}
```

## Tests Should Have Domain Meaning

Các bài kiểm thử mô hình của bạn nên mang ý nghĩa đối với các chuyên gia nghiệp vụ.

Các chuyên gia nghiệp vụ phi kỹ thuật — khi được trợ giúp một chút — khi đọc những bài kiểm thử dựa trên ví dụ thực tế này đã có thể hiểu được chính xác cách `BusinessPriority` được sử dụng, các loại kết quả mà nó tạo ra, hiểu rằng hành vi của nó được đảm bảo là không gây tác dụng phụ, và rằng nó tuân thủ chặt chẽ các khái niệm cùng chủ ý của Ubiquitous Language.

Quan trọng hơn, trạng thái của Value Object được đảm bảo là bất biến trong mọi trường hợp sử dụng. Các client có thể tạo ra kết quả từ các phép tính mức độ ưu tiên của bất kỳ số lượng hạng mục tồn đọng nào của sản phẩm, sắp xếp chúng, so sánh chúng và điều chỉnh `BusinessPriorityRatings` của từng mục khi cần.

## Implementation

Tôi thích ví dụ về `BusinessPriority` này vì nó thể hiện tất cả các đặc tính của một Value và thậm chí còn nhiều hơn thế. Bên cạnh việc chỉ ra cách thiết kế hướng tới tính bất biến, tính toàn vẹn khái niệm (conceptual wholeness), tính có thể thay thế (replaceability), tính bằng nhau theo giá trị (Value equality) và Side-Effect-Free Behavior, nó còn chứng minh cách bạn có thể sử dụng một kiểu Value như một Strategy (chiến lược) [Gamma et al.] (còn gọi là Policy - chính sách).

Khi từng phương thức kiểm thử được phát triển, nhóm đã hiểu rõ hơn về cách một client sẽ sử dụng một `BusinessPriority`, cho phép họ hiện thực hóa nó để hành xử đúng như những gì các bài kiểm thử đã khẳng định. Dưới đây là định nghĩa lớp cơ bản cùng với các hàm khởi tạo mà nhóm đã viết mã:

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000255_bd35ed753190c8be40cfc22ad26b788bdbbf9b55b0c83a8a78b3c703fd9e9430.png)

```java
public final class BusinessPriority implements Serializable {

    private static final long serialVersionUID = 1L;

    private BusinessPriorityRatings ratings;

    public BusinessPriority(BusinessPriorityRatings aRatings) {
        super();

        this.setRatings(aRatings);
    }

    public BusinessPriority(BusinessPriority aBusinessPriority) {
        this(aBusinessPriority.ratings());
    }
```

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000256_ace7b74e169d939d9047c1c81b5c59b1f8233110971375fa7bcef58265575753.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000257_f5e7b3c1b61ddcc280cc4b1d85e6ce6067f07d6f076e5bab9140eb0e206208a9.png)

Nhóm đã quyết định khai báo các kiểu Value của họ có khả năng tuần tự hóa (`Serializable`). Có những thời điểm một thể hiện Value cần phải được tuần tự hóa, chẳng hạn như khi nó được truyền đến một hệ thống từ xa, và điều này cũng có thể hữu ích cho một số chiến lược lưu trữ bền vững.

Bản thân `BusinessPriority` này được thiết kế để giữ một thuộc tính Value có tên là `ratings` thuộc kiểu `BusinessPriorityRatings` (không hiển thị ở đây). Thuộc tính `ratings` mô tả sự đánh đổi giữa giá trị kinh doanh và chi phí của việc triển khai hoặc không triển khai một hạng mục tồn đọng sản phẩm nhất định. Kiểu `BusinessPriorityRatings` cung cấp cho `BusinessPriority` các đánh giá về `benefit` (lợi ích), `cost` (chi phí), `penalty` (hình phạt/tổn thất) và `risk` (rủi ro), cho phép thực hiện một loạt các phép tính toán.

Thông thường, tôi hỗ trợ ít nhất hai hàm khởi tạo cho mỗi Value Object của mình. Hàm khởi tạo đầu tiên nhận đầy đủ các tham số cần thiết để suy ra và/hoặc thiết lập các thuộc tính trạng thái. Hàm khởi tạo chính này trước tiên khởi tạo trạng thái mặc định của nó. Việc khởi tạo thuộc tính cơ bản được thực hiện trước bằng cách gọi các hàm setter riêng tư (`private setters`). Tôi khuyến nghị sử dụng cơ chế tự ủy quyền (self-delegation) và minh họa cách sử dụng nó ở đây thông qua các setter riêng tư.

## Keeping Values Immutable

Chỉ có (các) hàm khởi tạo chính mới sử dụng cơ chế tự ủy quyền để thiết lập các thuộc tính. Không có phương thức nào khác được phép tự ủy quyền tới các phương thức setter. Vì tất cả các phương thức setter trong một Value Object luôn ở phạm vi riêng tư (`private`), nên các thuộc tính không có cơ hội bị lộ ra ngoài để người dùng thay đổi (mutation). Đây là hai yếu tố quan trọng trong việc duy trì tính bất biến của các Value.

Hàm khởi tạo thứ hai được sử dụng để sao chép một Value hiện có nhằm tạo ra một Value mới, hay còn được gọi là copy constructor (hàm khởi tạo sao chép). Hàm khởi tạo này thực hiện những gì được gọi là shallow copy (sao chép nông) khi nó tự ủy quyền cho hàm khởi tạo chính của nó, truyền vào dưới dạng tham số từng thuộc tính tương ứng của Value đang được sao chép. Chúng ta có thể thực hiện một deep copy (sao chép sâu) hoặc clone (nhân bản), trong đó tất cả các thuộc tính chứa bên trong đều được sao chép để tạo ra một đối tượng hoàn toàn duy nhất, nhưng vẫn bằng với giá trị của đối tượng được sao chép. Tuy nhiên, điều này nhiều khi tỏ ra vừa phức tạp vừa không cần thiết khi xử lý các Value. Nếu một deep copy từng cần đến, nó hoàn toàn có thể được bổ sung. Nhưng khi làm việc với các Value bất biến, việc chia sẻ các thuộc tính giữa các thể hiện với nhau không bao giờ là vấn đề.

Hàm khởi tạo thứ hai này, tức copy constructor, rất quan trọng đối với các bài kiểm thử đơn vị. Khi chúng ta kiểm thử một Value Object, chúng ta muốn đưa vào bước xác minh rằng nó là bất biến. Như đã minh họa trước đó, khi bài kiểm thử đơn vị bắt đầu, hãy tạo thể hiện Value Object kiểm thử mới và một bản sao của nó bằng cách sử dụng copy constructor, rồi khẳng định rằng hai thể hiện đó bằng nhau. Tiếp theo, kiểm thử Side-Effect-Free Behavior của thể hiện Value. Nếu tất cả các khẳng định mục tiêu kiểm thử đều vượt qua, khẳng định cuối cùng là thể hiện được kiểm thử và thể hiện được sao chép vẫn bằng nhau.

## Next, we implement the Strategy/Policy part of the Value type:

```java
public float costPercentage(BusinessPriorityTotals aTotals) {
    return (float) 100 * this.ratings().cost() / aTotals.totalCost();
}

public float priority(BusinessPriorityTotals aTotals) {
    return this.valuePercentage(aTotals) /
        (this.costPercentage(aTotals) + this.riskPercentage(aTotals));
}

public float riskPercentage(BusinessPriorityTotals aTotals) {
    return (float) 100 * this.ratings().risk() / aTotals.totalRisk();
}

public float totalValue() {
    return this.ratings().benefit() + this.ratings().penalty();
}

public float valuePercentage(BusinessPriorityTotals aTotals) {
    return (float) 100 * this.totalValue() / aTotals.totalValue();
}

public BusinessPriorityRatings ratings() {
    return this.ratings;
}
```

Một số hành vi tính toán yêu cầu một tham số thuộc kiểu `BusinessPriorityTotals`. Value này cung cấp một mô tả về tổng chi phí - rủi ro trên tất cả các hạng mục tồn đọng của sản phẩm. Các giá trị tổng là cần thiết khi tính toán tỷ lệ phần trăm và mức độ ưu tiên kinh doanh tổng thể so với tất cả các hạng mục tồn đọng khác. Không có hành vi nào trong số này sửa đổi trạng thái thể hiện của chính nó. Chúng ta khẳng định điều này từ bên ngoài trong các bài kiểm thử bằng cách so sánh trạng thái đã sao chép với trạng thái hiện tại sau khi thực thi mỗi hành vi.

Hiện tại không có Separated Interface (Giao diện Tách biệt) [Fowler, P of EAA] cho Strategy vì hiện tại chỉ có một hiện thực duy nhất. Chắc chắn theo thời gian điều đó sẽ thay đổi, và khách hàng của sản phẩm Agile PM SaaS sẽ được cung cấp các tùy chọn tính toán mức độ ưu tiên kinh doanh khác, mỗi tùy chọn có một hiện thực Strategy riêng.

Tên phương thức của các Side-Effect-Free Functions (hàm không gây tác dụng phụ) rất quan trọng. Mặc dù các phương thức này đều trả về các Value (vì chúng là các phương thức truy vấn CQS - Command-Query Separation / Phân tách Lệnh và Truy vấn), chúng cố tình tránh việc sử dụng quy ước đặt tên JavaBean với tiền tố `get-`. Cách tiếp cận đơn giản nhưng hiệu quả này trong thiết kế đối tượng giúp Value Object luôn trung thành với Ubiquitous Language. Việc sử dụng `getValuePercentage()` là một câu lệnh kỹ thuật của máy tính, nhưng `valuePercentage()` lại là một cách diễn đạt ngôn ngữ lưu loát, dễ đọc đối với con người.

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000258_2283d74f9ea51abcc4dab0e529aaddee03899a578a47ffe7fa2a06f3965d3715.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000259_4a85423f605a809b7366dfeda368ef3bede354df0454846b9980a193583ad296.png)

## Where Did My Fluent Java Go?

Tôi nghĩ rằng đặc tả JavaBean đã có tác động tiêu cực đến thiết kế đối tượng, một tác động không hề thúc đẩy các nguyên lý của Domain-Driven Design hay thiết kế hướng đối tượng tốt nói chung. Hãy xem xét API Java tồn tại trước đặc tả JavaBean. Lấy `java.lang.String` làm một ví dụ. Chỉ có một vài phương thức truy vấn trên lớp `String` được đặt tiền tố bằng `get`. Hầu hết các phương thức truy vấn được đặt tên lưu loát hơn, chẳng hạn như `charAt()`, `compareTo()`, `concat()`, `contains()`, `endsWith()`, `indexOf()`, `length()`, `replace()`, `startsWith()`, `substring()`, và những phương thức tương tự. Không hề có "mùi hôi của mã nguồn" (code smell) kiểu JavaBean ở đó! Dĩ nhiên, chỉ riêng ví dụ này không chứng minh được quan điểm của tôi. Dẫu vậy, sự thật là các API của Java kể từ khi có đặc tả JavaBean đã bị ảnh hưởng nặng nề và thiếu đi tính lưu loát trong cách biểu đạt. Một biểu đạt ngôn ngữ lưu loát, dễ đọc cho con người là một phong cách rất đáng để theo đuổi.

Nếu bạn lo lắng về các công cụ phụ thuộc vào đặc tả JavaBean, luôn có những giải pháp. Ví dụ, Hibernate hỗ trợ truy cập ở cấp độ trường (field-level access) (các thuộc tính đối tượng). Do đó, đối với Hibernate, các phương thức của bạn có thể được đặt tên theo ý muốn mà không gây tác động tiêu cực đến việc lưu trữ bền vững.

Tuy nhiên, với các công cụ khác, có thể có mặt hạn chế khi thiết kế với các interface mang tính biểu đạt cao. Ví dụ, nếu bạn muốn sử dụng Java EL (Expression Language) hoặc OGNL chuẩn, bạn sẽ không thể hiển thị trực tiếp các kiểu như vậy. Bạn sẽ phải sử dụng một phương tiện khác, chẳng hạn như Data Transfer Object (DTO - Đối tượng Truyền tải Dữ liệu) [Fowler, P of EAA] với các getter, để chuyển các thuộc tính của Value Object lên giao diện người dùng. Vì DTO là một mẫu phổ biến, mặc dù thường không cần thiết về mặt kỹ thuật, một số người có thể thấy điều này không có gì to tát. Nếu DTO không phải là lựa chọn dành cho bạn, vẫn còn những cách khác. Hãy xem xét Presentation Model như được thảo luận trong Application (Ứng dụng) (14). Vì Presentation Model của bạn có thể đóng vai trò như một Adapter (Bộ điều hợp) [Gamma et al.], nó có thể hiển thị các getter cho các view sử dụng EL chẳng hạn. Nhưng nếu mọi giải pháp khác đều thất bại, bạn có thể phải miễn cưỡng thiết kế các đối tượng miền của mình kèm theo các getter.

Nếu bạn đi đến kết luận đó, bạn vẫn không nên thiết kế các Value Object với đầy đủ các khả năng của JavaBean vốn cho phép trạng thái của chúng được khởi tạo thông qua các public setter. Điều đó sẽ vi phạm đặc tính bất biến thiết yếu của Value.

Tập hợp các phương thức tiếp theo bao gồm các hàm ghi đè đối tượng chuẩn: `equals()`, `hashCode()`, và `toString()`:

```java
@Override
public boolean equals(Object anObject) {
    boolean equalObjects = false;

    if (anObject != null && this.getClass() == anObject.getClass()) {
        BusinessPriority typedObject = (BusinessPriority) anObject;
        equalObjects = this.ratings().equals(typedObject.ratings());
    }

    return equalObjects;
}

@Override
public int hashCode() {
    int hashCodeValue =
        + (169065 * 179)
        + this.ratings().hashCode();

    return hashCodeValue;
}

@Override
public String toString() {
    return "BusinessPriority"
        + " ratings = " + this.ratings();
}
```

Phương thức `equals()` đáp ứng yêu cầu của Value Object về việc kiểm tra tính bằng nhau theo giá trị, một trong năm đặc tính của Value. Ở đây chúng tôi luôn loại bỏ các tham số `null` khỏi phép so sánh bằng. Lớp của tham số phải cùng một lớp với Value. Nếu chúng cùng lớp, từng thuộc tính sẽ được so sánh trong cả hai Value. Nếu từng thuộc tính được xác nhận là bằng với thuộc tính tương ứng của nó, thì Whole Values (toàn thể các giá trị) được coi là bằng nhau.

Theo các chuẩn của Java, `hashCode()` có cùng hợp đồng với `equals()` ở chỗ tất cả các Value bằng nhau cũng tạo ra các giá trị hash code bằng nhau.

Không có gì đặc biệt về `toString()`. Nó tạo ra một biểu diễn có thể đọc được đối với con người về trạng thái thể hiện của Value. Bạn có thể thiết kế định dạng biểu diễn tùy theo nhu cầu.

Còn một vài phương thức còn lại cần xem xét:

```java
protected BusinessPriority() {
    super();
}

private void setRatings(BusinessPriorityRatings aRatings) {
    if (aRatings == null) {
```

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000260_6f2ac0863d2d6136f41a6639acf565907a16742a83cab397e8301015c9b57890.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000261_938a779c42faaa5fc5a2c8936db040a92f1ec06f0fa41cc85462016253cb6bd0.png)

```java
        throw new IllegalArgumentException(
            "The ratings are required.");
    }

    this.ratings = aRatings;
}
}
```

Hàm khởi tạo không tham số (zero-argument constructor) được cung cấp vì lợi ích của các công cụ framework yêu cầu nó, chẳng hạn như Hibernate. Vì hàm khởi tạo không tham số luôn được ẩn đi, nên không có nguy cơ các client của mô hình tạo ra các thể hiện không hợp lệ. Hibernate hoạt động hoàn hảo với các hàm khởi tạo và các accessor bị ẩn. Hàm khởi tạo này cho phép Hibernate và các công cụ khác tạo ra các thể hiện của kiểu khi chúng đang được tái tạo (reconstituted) từ, ví dụ, kho lưu trữ bền vững. Các công cụ sử dụng hàm khởi tạo không tham số để tạo ra một thể hiện rỗng ban đầu và sau đó gọi từng setter của thuộc tính để nạp dữ liệu (hydrate) cho đối tượng. Tùy chọn khác là bạn có thể bảo Hibernate bỏ qua các phương thức setter và thiết lập trực tiếp các thuộc tính, như trường hợp của mô hình này vì nó không cung cấp một giao diện JavaBean hoàn chỉnh. Xin nhắc lại một lần nữa, các client của mô hình chỉ sử dụng các hàm khởi tạo công khai (public constructors), không bao giờ dùng hàm khởi tạo ẩn.

Cuối cùng, định nghĩa lớp kết thúc bằng setter thuộc tính cho `ratings`. Một trong những thế mạnh của việc tự đóng gói/ủy quyền (self-encapsulation/delegation) được thể hiện trong phương thức này. Một phương thức accessor — getter hoặc setter — không nhất thiết phải bị giới hạn ở việc gán một trường thể hiện. Nó cũng có thể thực hiện các Assertion (khẳng định/ràng buộc tính đúng đắn) [Evans] quan trọng, một yếu tố then chốt dẫn đến sự phát triển phần mềm thành công nói chung và các mô hình DDD nói riêng.

Assertion kiểm tra tính hợp lệ của tham số được gọi là guard (chốt chặn), bởi vì nó bảo vệ phương thức khỏi việc phải tiếp nhận dữ liệu rõ ràng không hợp lệ. Các guard có thể và nên được sử dụng trong bất kỳ phương thức nào khi các tham số sai lệch sẽ gây ra những vấn đề nghiêm trọng hơn về sau nếu tính đúng đắn cứ mặc nhiên được công nhận. Ở đây, hàm setter khẳng định rằng tham số `aRatings` không được là null, và nếu tình cờ bị null, nó sẽ ném ra một ngoại lệ `IllegalArgumentException`. Đúng là hàm setter này về mặt logic chỉ được sử dụng một lần duy nhất trong suốt vòng đời của Value. Tuy nhiên, Assertion vẫn là một chốt chặn được đặt đúng chỗ. Bạn cũng sẽ thấy những ưu điểm của cơ chế tự ủy quyền được thể hiện ở những nơi khác. Cụ thể, chương Entities (5) sẽ giải thích kỹ thuật này một cách thấu đáo như một phần của cuộc thảo luận về xác thực (validation).

## Persisting Value Objects

Có rất nhiều cách để lưu trữ bền vững các thể hiện Value Object vào một kho lưu trữ bền vững. Theo nghĩa chung, việc này bao gồm việc tuần tự hóa đối tượng sang một định dạng văn bản hoặc nhị phân nào đó và lưu nó vào đĩa. Tuy nhiên, vì chúng ta không bận tâm đến việc lưu trữ bền vững các thể hiện Value riêng lẻ một cách độc lập, tôi sẽ không tập trung vào việc lưu trữ bền vững cho mục đích chung. Thay vào đó, chúng ta quan tâm nhiều hơn đến việc lưu trữ bền vững các Value cùng với trạng thái của các thể hiện Aggregate chứa chúng. Các cách tiếp cận sau đây giả định rằng một Entity cha cuối cùng sẽ nắm giữ các tham chiếu đến các thể hiện Value được lưu trữ bền vững. Tất cả các ví dụ sau đây đều dựa trên giả định rằng một Aggregate đang được thêm vào hoặc đọc từ Repository (Kho lưu trữ) (12) của nó, và các Value chứa bên trong nó được lưu trữ bền vững và tái tạo ở hậu trường cùng với Entity — chẳng hạn như Aggregate Root (Gốc Cụm thực thể) — chứa chúng.

Lưu trữ bền vững bằng ORM (Object-relational mapping - ánh xạ đối tượng - quan hệ, chẳng hạn như Hibernate) rất phổ biến và được sử dụng rộng rãi. Tuy nhiên, việc sử dụng một ORM để ánh xạ mọi lớp thành một bảng và mọi thuộc tính thành một cột sẽ làm tăng thêm độ phức tạp, điều có thể là không đáng có. Xu hướng sử dụng cơ sở dữ liệu NoSQL và các kho lưu trữ khóa - giá trị (key-value stores) đang ngày càng gia tăng nhờ khả năng cung cấp lưu trữ cấp doanh nghiệp với hiệu năng cao, khả năng mở rộng, chịu lỗi và tính sẵn sàng cao. Hơn nữa, các kho lưu trữ khóa - giá trị có thể đơn giản hóa đáng kể việc lưu trữ bền vững Aggregate. Trong chương này, tôi vẫn gắn bó với việc lưu trữ bền vững dựa trên ORM. Bởi vì các kho lưu trữ khóa - giá trị NoSQL lưu trữ Aggregate đặc biệt xuất sắc, tôi sẽ dành sự chú ý cho phong cách đó trong chương Repositories (12).

Nhưng trước khi chúng ta đi sâu vào các ví dụ lưu trữ bền vững Value bằng ORM, có một cam kết mô hình hóa sống còn cần phải được hiểu rõ và tuân thủ một cách mẫn cán. Vì vậy, để bắt đầu, chúng ta hãy giải quyết những gì có thể xảy ra khi việc mô hình hóa dữ liệu (trái ngược với mô hình hóa miền nghiệp vụ) có ảnh hưởng không thích hợp lên mô hình miền của bạn, và những gì có thể làm để loại bỏ ảnh hưởng sai lầm và tai hại này.

## Reject Undue Influence of Data Model Leakage

Có lẽ phần lớn các lần một Value Object được lưu trữ bền vững vào một kho dữ liệu (ví dụ, sử dụng một công cụ ORM cùng với một cơ sở dữ liệu quan hệ), nó được lưu trữ theo cách phi chuẩn hóa (denormalized); nghĩa là, các thuộc tính của nó được lưu trữ trong cùng một hàng của bảng cơ sở dữ liệu với đối tượng Entity cha của nó. Điều này giúp cho việc lưu trữ và truy xuất các Value trở nên sạch sẽ và tối ưu, đồng thời ngăn chặn bất kỳ sự rò rỉ nào từ kho lưu trữ bền vững vào mô hình. Thật là vừa thú vị vừa nhẹ nhõm khi các Value có thể được lưu trữ bền vững theo cách này.

Tuy nhiên, có những lúc một Value Object trong mô hình bắt buộc phải được lưu trữ như một Entity xét theo góc độ của một kho lưu trữ bền vững quan hệ. Nói cách khác, khi được lưu trữ bền vững, một thể hiện của một kiểu Value Object cụ thể sẽ chiếm một hàng riêng trong một bảng cơ sở dữ liệu quan hệ tồn tại dành riêng cho kiểu của nó, và nó sẽ có cột khóa chính (primary key) cơ sở dữ liệu của riêng mình. Điều này xảy ra, ví dụ, khi hỗ trợ một tập hợp (collection) các thể hiện Value Object bằng ORM. Trong những trường hợp như vậy, dữ liệu lưu trữ bền vững của kiểu Value được mô hình hóa như một thực thể cơ sở dữ liệu.

Liệu đây có phải là dấu hiệu cho thấy đối tượng mô hình miền nên phản ánh thiết kế của mô hình dữ liệu và trở thành một Entity thay vì một Value hay không? Không. Khi bạn đối mặt với hậu quả của sự bất đối xứng này (impedance mismatch - sự lệch pha giữa mô hình đối tượng và quan hệ), điều quan trọng là phải duy trì góc nhìn của mô hình miền thay vì góc nhìn của việc lưu trữ bền vững. Để giữ vững góc nhìn của bạn trên mô hình miền, bạn có thể tự hỏi bản thân những câu hỏi sau:

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000262_b2414d293177091a8f848981a22a472fca674629a493391fb5701f709d8563f7.png)

1. Khái niệm tôi đang mô hình hóa là một sự vật trong miền nghiệp vụ hay nó đo lường, định lượng hoặc mô tả một sự vật như một trong những thuộc tính của sự vật đó?
2. Nếu được mô hình hóa chính xác để mô tả một phần tử của miền nghiệp vụ, khái niệm mô hình này có phải sở hữu tất cả hoặc hầu hết các đặc tính của giá trị đã được nêu ra trước đây không?
3. Có phải tôi đang cân nhắc việc sử dụng một Entity trong mô hình chỉ vì mô hình dữ liệu bên dưới bắt buộc phải lưu trữ đối tượng mô hình miền thành một thực thể hay không?
4. Có phải tôi đang sử dụng một Entity vì mô hình miền đòi hỏi danh tính duy nhất, tôi quan tâm đến các thể hiện riêng lẻ và tôi phải quản lý một chuỗi liên tục các thay đổi trong suốt vòng đời của đối tượng hay không?

Nếu các câu trả lời của bạn là: "Mô tả, Có, Có, và Không", bạn nên sử dụng một Value Object. Hãy mô hình hóa kho lưu trữ bền vững theo cách cần thiết để xử lý việc lưu trữ đối tượng, nhưng đừng để điều đó ảnh hưởng đến cách nhóm của bạn nhận thức khái niệm thuộc tính Value trong mô hình miền.

## The Data Model Should Be Subordinate

Hãy thiết kế mô hình dữ liệu của bạn vì lợi ích của mô hình miền, chứ không phải thiết kế mô hình miền vì lợi ích của mô hình dữ liệu.

Nếu có thể, hãy luôn thiết kế mô hình dữ liệu vì lợi ích của mô hình miền, chứ không phải mô hình miền vì lợi ích của mô hình dữ liệu. Nếu làm theo vế đầu, bạn sẽ duy trì được góc nhìn của mô hình miền. Nếu làm theo vế sau, bạn sẽ duy trì góc nhìn của việc lưu trữ bền vững và mô hình miền của bạn sẽ có xu hướng chỉ đóng vai trò như một hình chiếu (projection) đơn thuần của mô hình dữ liệu. Khi bạn rèn luyện tư duy của mình để suy nghĩ theo góc độ của mô hình miền — tư duy DDD (DDD-think) — thay vì mô hình dữ liệu, bạn sẽ tránh được những hậu quả tiêu cực của việc rò rỉ mô hình dữ liệu. Xem chương Entities (5) để biết thêm thảo luận về tư duy DDD.

Dĩ nhiên, có những lúc tính toàn vẹn tham chiếu của cơ sở dữ liệu (referential integrity) là quan trọng (chẳng hạn như đối với các khóa ngoại - foreign keys). Chắc chắn, bạn muốn các cột khóa phải được đánh chỉ mục (indexed) đúng cách. Rõ ràng, chắc chắn có nhu cầu hỗ trợ các công cụ báo cáo thông minh doanh nghiệp (business intelligence) hoạt động trên dữ liệu kinh doanh của bạn. Bạn có thể kích hoạt tất cả các khía cạnh này ở những nơi phù hợp và cần thiết. Đa số đều đi đến kết luận rằng việc báo cáo và phân tích thông minh doanh nghiệp không nên hoạt động trực tiếp trên dữ liệu sản xuất (production data) của bạn mà thay vào đó nên có một mô hình dữ liệu chuyên dụng, được thiết kế đặc thù. Việc tuân theo tâm thế mang tính chiến lược hơn này sẽ giải phóng bạn để thiết kế mô hình dữ liệu nền tảng cho mô hình miền sao cho hỗ trợ tốt nhất cho các nỗ lực DDD của bạn.

Bất kể mô hình dữ liệu của bạn sử dụng những khía cạnh kỹ thuật nào, các thực thể, khóa chính, tính toàn vẹn tham chiếu và các chỉ mục của nó đơn giản là không được phép chi phối cách bạn mô hình hóa các đối tượng miền. DDD không nói về việc cấu trúc dữ liệu theo cách chuẩn hóa (normalized). Nó nói về việc mô hình hóa Ubiquitous Language trong một Bounded Context nhất quán. Tôi khuyến khích bạn tuân thủ DDD chứ không phải cấu trúc dữ liệu. Khi làm như vậy, bạn nên có những bước đi khôn ngoan để che giấu mọi tàn tích của sự rò rỉ mô hình dữ liệu (vốn sẽ xảy ra ở mức tối thiểu khi sử dụng một ORM) khỏi mô hình miền và các client của nó. Đây là điều tôi sẽ thảo luận trong phần tiếp theo.

## ORM and Single Value Objects

Việc lưu trữ bền vững một thể hiện Value Object đơn lẻ vào cơ sở dữ liệu thường rất đơn giản. Ở đây trọng tâm của tôi là việc sử dụng Hibernate cùng với cơ sở dữ liệu quan hệ MySQL. Ý tưởng cơ bản là lưu trữ từng thuộc tính của Value vào các cột riêng biệt trong hàng nơi đối tượng Entity cha của nó được lưu trữ. Nói cách khác, một Value Object đơn lẻ được phi chuẩn hóa vào hàng của Entity cha. Việc áp dụng quy ước đặt tên cột mang lại nhiều lợi thế để xác định rõ ràng và chuẩn hóa cách đặt tên cho các đối tượng được tuần tự hóa. Tôi xin trình bày một quy ước đặt tên cho Value Object được lưu trữ bền vững tại đây.

Khi sử dụng Hibernate để lưu trữ bền vững một thể hiện đơn lẻ của một Value Object, hãy sử dụng phần tử ánh xạ `component`. Phần tử `component` được sử dụng vì nó cho phép Value được ánh xạ trực tiếp vào hàng của bảng Entity cha theo cách phi chuẩn hóa. Đây là một kỹ thuật tuần tự hóa tối ưu mà vẫn cho phép các Value được đưa vào các truy vấn SQL. Dưới đây là phần tài liệu ánh xạ Hibernate mô tả việc ánh xạ Value Object `BusinessPriority` được giữ bởi Entity cha của nó, lớp `BacklogItem`:

```xml
<component name="businessPriority" class="com.saasovation.agilepm.domain.model.product.BusinessPriority">
    <component name="ratings" class="com.saasovation.agilepm.domain.model.product.BusinessPriorityRatings">
        <property name="benefit" column="business_priority_ratings_benefit" type="int" update="true" insert="true" lazy="false" />
        <property name="cost" column="business_priority_ratings_cost"
```

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000263_6f5a92af5ddb99d5162510c774085bb6e2120f82a19b444d80998d90885c2c12.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000264_749f5ca0e92f7eb39e6c504ed59569d4213420dd1ceccf348f704731ff9aecda.png)

```xml
                  type="int" update="true" insert="true" lazy="false" />
        <property name="penalty" column="business_priority_ratings_penalty" type="int" update="true" insert="true" lazy="false" />
        <property name="risk" column="business_priority_ratings_risk" type="int" update="true" insert="true" lazy="false" />
    </component>
</component>
```

Đây là một ví dụ điển hình vì nó thể hiện một cấu hình ánh xạ Value Object đơn giản, nhưng lại chứa một thể hiện Value Object con bên trong. Hãy nhớ lại rằng `BusinessPriority` có một thuộc tính Value duy nhất là `ratings` và không có thêm thuộc tính nào khác. Do đó, trong phần mô tả ánh xạ, phần tử `component` bên ngoài có một phần tử `component` lồng bên trong. Điều này được sử dụng để phi chuẩn hóa thuộc tính Value `ratings` chứa bên trong thuộc kiểu `BusinessPriorityRatings`. Vì `BusinessPriority` không có thuộc tính nào của riêng nó, nên không có thuộc tính nào được ánh xạ trong `component` bên ngoài. Thay vào đó, chúng tôi lồng ngay phần ánh xạ thuộc tính Value `ratings` của nó. Cuối cùng, chúng tôi thực sự chỉ lưu trữ bốn thuộc tính số nguyên của thể hiện `BusinessPriorityRatings` vào bốn cột riêng biệt của bảng `tbl_backlog_item`. Vì vậy, chúng tôi ánh xạ hai Value Object phần tử `component`: một đối tượng không có thuộc tính riêng và một Value bên trong có bốn thuộc tính.

Lưu ý cách sử dụng quy ước đặt tên cột chuẩn cho từng phần tử `property` của Hibernate. Quy ước đặt tên dựa trên đường dẫn điều hướng (navigation path) từ Value cha cao nhất xuống các thuộc tính riêng lẻ. Ví dụ, hãy xem xét đường dẫn điều hướng từ `BusinessPriority` xuống thuộc tính `benefit` của thể hiện `ValueCostRiskRatings`. Về mặt logic, nó là:

```
businessPriority.ratings.benefit
```

Để biểu diễn đường dẫn điều hướng này thành một tên cột quan hệ duy nhất, tôi sử dụng như sau:

business_priority_ratings_benefit

Dĩ nhiên, bạn có thể sử dụng một tên mang tính đại diện khác nếu muốn. Có thể bạn thích một tên kết hợp giữa camelCase với dấu gạch dưới:

businessPriority_ratings_benefit

Trong tâm trí bạn, ký hiệu mẫu này có thể thể hiện việc điều hướng tốt hơn. Tôi đã chuẩn hóa theo kiểu toàn bộ bằng chữ thường kèm dấu gạch dưới (snake_case) vì nó nghiêng nhiều hơn về tên cột SQL truyền thống thay vì tên đối tượng. Định nghĩa bảng cơ sở dữ liệu MySQL tương ứng bao gồm các cột sau:

```sql
CREATE TABLE `tbl_backlog_item` (
    ...
    `business_priority_ratings_benefit` int NOT NULL,
    `business_priority_ratings_cost` int NOT NULL,
    `business_priority_ratings_penalty` int NOT NULL,
    `business_priority_ratings_risk` int NOT NULL,
    ...
) ENGINE=InnoDB;
```

Cùng với nhau, cấu hình ánh xạ Hibernate và định nghĩa bảng cơ sở dữ liệu quan hệ cung cấp một đối tượng lưu trữ bền vững vừa tối ưu vừa có thể truy vấn được. Bởi vì các thuộc tính của Value được phi chuẩn hóa vào hàng trong bảng của Entity cha của chúng, cơ sở dữ liệu không cần sử dụng các phép kết nối bảng (join) để truy xuất ngay cả một thể hiện Value lồng nhau sâu. Khi bạn chỉ định một truy vấn HQL (Hibernate Query Language), Hibernate có thể dễ dàng ánh xạ từ biểu thức đối tượng của một thuộc tính đối tượng thành một biểu thức truy vấn SQL tối ưu sử dụng một cột, nơi:

```
businessPriority.ratings.benefit trở thành business_priority_ratings_benefit
```

Do đó, mặc dù có sự bất đối xứng rõ rệt giữa các đối tượng và cơ sở dữ liệu quan hệ (impedance mismatch), chúng ta đã hiện thực hóa được một trong những phương thức ánh xạ hiệu quả và tối ưu nhất có thể.

## ORM and Many Values Serialized into a Single Column

Có những thách thức đặc thù liên quan đến việc ánh xạ một tập hợp (collection) gồm nhiều Value Object vào một cơ sở dữ liệu quan hệ bằng ORM. Nói cho rõ ràng, khi tôi nói tập hợp nghĩa là tôi đang đề cập đến một `List` hoặc `Set` được giữ bởi một Entity và chứa không, một, hoặc nhiều thể hiện Value. Những thách thức này không phải là không thể vượt qua, nhưng sự bất đối xứng đối tượng - quan hệ (object-relational impedance mismatch) trở nên hiển hiện rõ mồn một ở đây.

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000265_dac50871ad69e8af7e8af8b3e31cadb73497acbfc05ceadf865833b8300714d8.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000266_d03acfdb385e3d7d7784d0fcfa8f1facea37b62bd3c19e894505616b72a30b6c.png)